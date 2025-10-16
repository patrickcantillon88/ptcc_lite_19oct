"""
KS2Agents data migration into PTCC database

Features:
- Structured logging with before/after counts
- Reads Example docs JSON sources (rag_data.json, raw_rag_data.json)
- Maps entries into Communication records
- Duplicate prevention by (subject, content) match
- Dry-run support (no DB writes)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from typing import Iterable, List, Tuple

from sqlalchemy.orm import Session

from ..core.logging_config import get_logger, setup_logging
from ..core.database import SessionLocal, create_tables, get_database_stats
from ..models.database_models import Communication


logger = get_logger("ks2agents_migrate")


def compute_text_fingerprint(text: str) -> str:
    """Create a stable fingerprint for de-duplication based on content."""
    normalized = " ".join((text or "").split()).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_json_array(file_path: str) -> List[dict]:
    """Load a JSON array file, returning empty list if not found or invalid."""
    if not os.path.exists(file_path):
        logger.warning(f"Source not found: {file_path}")
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        logger.warning(f"Expected JSON array in {file_path}, got {type(data)}")
        return []
    except Exception as exc:
        logger.error(f"Failed to read {file_path}: {exc}")
        return []


def summarize_subject(content: str, fallback: str = "KS2Agents Import") -> str:
    """Generate a short subject line from content."""
    if not content:
        return fallback
    text = " ".join(content.split())
    if len(text) <= 80:
        return text
    return text[:77] + "..."


def infer_source(meta: dict | None) -> str:
    """Map metadata to Communication.source values."""
    if not meta:
        return "manual"
    src_type = str(meta.get("type", "")).lower()
    if src_type in {"email"}:
        return "email"
    if src_type in {"google_doc", "gdoc", "doc", "docx", "pdf"}:
        return "google_doc"
    return "manual"


def map_json_entry_to_communication(entry: dict) -> Communication:
    """Map a KS2Agents JSON entry into a Communication ORM instance (not added to session)."""
    content = entry.get("content") or ""
    metadata = entry.get("metadata") or {}

    subject = summarize_subject(content)
    source = infer_source(metadata)

    # Use now when no explicit time available
    received_date = datetime.utcnow()

    return Communication(
        source=source,
        campus=None,
        subject=subject,
        sender=metadata.get("source") if isinstance(metadata.get("source"), str) else None,
        content=content,
        category="fyi",
        received_date=received_date,
        action_required=False,
        read=False,
        archived=False,
    )


def get_existing_fingerprints(db: Session) -> set[str]:
    """Build a set of fingerprints for existing communications using (subject+content)."""
    fingerprints: set[str] = set()
    for subject, content in db.query(Communication.subject, Communication.content):
        fingerprints.add(compute_text_fingerprint((subject or "") + "\n" + (content or "")))
    return fingerprints


def migrate_communications(
    db: Session, sources: Iterable[str], dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Migrate communications from given JSON array files.

    Returns: (seen, inserted, duplicates)
    """
    total_seen = 0
    total_inserted = 0
    total_duplicates = 0

    existing_fps = get_existing_fingerprints(db)

    for path in sources:
        entries = load_json_array(path)
        if not entries:
            continue

        logger.info(f"Loaded {len(entries)} entries from {path}")
        for entry in entries:
            total_seen += 1
            temp_comm = map_json_entry_to_communication(entry)
            fp = compute_text_fingerprint((temp_comm.subject or "") + "\n" + (temp_comm.content or ""))
            if fp in existing_fps:
                total_duplicates += 1
                continue

            if dry_run:
                # Do not add, just count as would-insert
                total_inserted += 1
                continue

            db.add(temp_comm)
            total_inserted += 1
            existing_fps.add(fp)

    if not dry_run and total_inserted:
        db.commit()

    return total_seen, total_inserted, total_duplicates


def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Migrate KS2Agents data into PTCC database")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing to the database",
    )
    parser.add_argument(
        "--example-dir",
        default=os.path.join("ptcc", "Example docs"),
        help="Directory containing KS2Agents example files",
    )
    args = parser.parse_args()

    logger.info("Starting KS2Agents migration")
    create_tables()

    before_stats = get_database_stats()
    logger.info(f"Before migration counts: {before_stats}")

    json_sources = [
        os.path.join(args.example_dir, "rag_data.json"),
        os.path.join(args.example_dir, "raw_rag_data.json"),
    ]

    db = SessionLocal()
    try:
        seen, inserted, duplicates = migrate_communications(db, json_sources, dry_run=args.dry_run)
        logger.info(
            f"Communications processed: seen={seen}, inserted={inserted}, duplicates={duplicates}, dry_run={args.dry_run}"
        )
    except Exception as exc:
        logger.error(f"Migration failed: {exc}")
        db.rollback()
        raise
    finally:
        db.close()

    after_stats = get_database_stats() if not args.dry_run else before_stats
    logger.info(f"After migration counts: {after_stats}")

    # Simple record count validation (communications table)
    before_comm = before_stats.get("communications", 0)
    after_comm = after_stats.get("communications", 0)
    expected_after = before_comm + inserted if not args.dry_run else before_comm
    if after_comm != expected_after:
        logger.warning(
            f"Record count validation mismatch: expected communications={expected_after}, actual={after_comm}"
        )
    else:
        logger.info("Record count validation succeeded for communications")

    logger.info("KS2Agents migration completed")


if __name__ == "__main__":
    main()


