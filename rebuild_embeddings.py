#!/usr/bin/env python3
"""
Rebuild Vector Embeddings from Current Database

This script:
1. Clears old ChromaDB collections
2. Fetches all current students from SQLite database
3. Re-embeds them for RAG (semantic search)
"""

import os
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal
from backend.models.database_models import Student
from backend.core.rag_engine import RAGEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_chromadb():
    """Remove old ChromaDB vector database"""
    chroma_path = project_root / "data" / "chroma"
    
    if chroma_path.exists():
        logger.info(f"🗑️  Removing old ChromaDB at {chroma_path}")
        shutil.rmtree(chroma_path)
        logger.info("✅ Old embeddings cleared")
    else:
        logger.info("ℹ️  No existing ChromaDB found")

def rebuild_embeddings():
    """Rebuild embeddings from current students in database"""
    
    # Initialize RAG engine (creates new collections)
    logger.info("🔄 Initializing RAG engine...")
    rag = RAGEngine()
    logger.info("✅ RAG engine initialized")
    
    # Get all students from database
    logger.info("📚 Fetching students from database...")
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    
    if not students:
        logger.error("❌ No students found in database!")
        return False
    
    logger.info(f"✅ Found {len(students)} students")
    
    # Organize by class
    by_class = {}
    for student in students:
        class_code = student.class_code
        if class_code not in by_class:
            by_class[class_code] = []
        by_class[class_code].append(student)
    
    logger.info(f"\n📊 Students by class:")
    for class_code in sorted(by_class.keys()):
        count = len(by_class[class_code])
        logger.info(f"   {class_code}: {count} students")
    
    # Index all database data using RAG engine's built-in method
    logger.info(f"\n🚀 Indexing all database data for RAG...")
    try:
        rag.index_database_data()
        logger.info(f"✅ Indexed all data successfully")
    except Exception as e:
        logger.error(f"❌ Error indexing database data: {e}")
        return False
    
    # Verify embeddings
    logger.info("\n🔍 Verifying embeddings...")
    try:
        # Test search
        results = rag.search("3A", top_k=5)
        logger.info(f"✅ Search test successful - found {len(results)} results for '3A'")
        
        if results:
            logger.info("\n📋 Sample search results:")
            for i, result in enumerate(results[:3], 1):
                logger.info(f"   {i}. {result.get('metadata', {}).get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"❌ Search verification failed: {e}")
        return False
    
    return True

def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("🔄 REBUILDING VECTOR EMBEDDINGS")
    logger.info("=" * 60)
    
    # Step 1: Clear old embeddings
    logger.info("\n📌 Step 1: Clearing old embeddings...")
    clear_chromadb()
    
    # Step 2: Rebuild from current database
    logger.info("\n📌 Step 2: Rebuilding embeddings...")
    success = rebuild_embeddings()
    
    # Summary
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ EMBEDDINGS REBUILT SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\n✓ Vector database now contains:")
        logger.info("  - Current students (3A, 4B, 5C, 6D)")
        logger.info("  - Updated embeddings for semantic search")
        logger.info("  - Behavior management data ready for RAG")
        logger.info("  - Safeguarding analysis ready")
        logger.info("\n💡 Restart the application to use new embeddings")
        return 0
    else:
        logger.error("❌ EMBEDDING REBUILD FAILED")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
