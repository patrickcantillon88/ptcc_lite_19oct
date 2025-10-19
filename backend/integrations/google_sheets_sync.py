"""
Google Sheets Integration for PTCC
Syncs student data from Google Sheets into PTCC database
One-way import: Sheet → PTCC
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

# Google Sheets API
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import gspread

from ..core.database import SessionLocal
from ..models.database_models import Student, DataSourceMetadata
from ..core.logging_config import get_logger

logger = get_logger("integrations.google_sheets")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleSheetsSync:
    """Sync student data from Google Sheets"""
    
    def __init__(self, sheet_id: str, sheet_name: str = "Students"):
        """
        Initialize Google Sheets sync
        
        Args:
            sheet_id: Google Sheet ID (from URL)
            sheet_name: Name of the sheet tab to sync
        """
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.client = self._authenticate()
        self.last_sync_hash = None
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Use service account credentials from environment
            service_account_info = {
                "type": os.getenv("GOOGLE_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            }
            
            creds = Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )
            
            client = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets")
            return client
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def get_sheet_data(self) -> List[Dict]:
        """
        Fetch all data from Google Sheet
        
        Returns:
            List of dictionaries with row data
        """
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.worksheet(self.sheet_name)
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                logger.warning("Sheet is empty or has no data rows")
                return []
            
            # First row is headers
            headers = all_values[0]
            
            # Convert to list of dicts
            data = []
            for row in all_values[1:]:
                row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                data.append(row_dict)
            
            logger.info(f"Retrieved {len(data)} rows from Google Sheet")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching sheet data: {e}")
            raise
    
    def parse_student_row(self, row: Dict) -> Optional[Dict]:
        """
        Parse a sheet row into student data
        
        Expected columns in sheet:
        - name: Student name
        - class_code: Class code (e.g., "3A")
        - year_group: Year group (e.g., "3")
        - campus: Campus name
        - support_level: Support level (0-4)
        - support_notes: Any special notes
        """
        try:
            # Validate required fields
            if not row.get("name") or not row.get("class_code"):
                logger.warning(f"Skipping row - missing required fields: {row}")
                return None
            
            return {
                "name": row.get("name", "").strip(),
                "class_code": row.get("class_code", "").strip(),
                "year_group": row.get("year_group", "").strip(),
                "campus": row.get("campus", "").strip(),
                "support_level": int(row.get("support_level", 0)),
                "support_notes": row.get("support_notes", "").strip(),
                "source_id": row.get("sheet_row_id", ""),  # Optional: track row ID
            }
        except Exception as e:
            logger.error(f"Error parsing student row: {e}")
            return None
    
    def sync(self) -> Dict:
        """
        Perform full sync from Google Sheet
        
        Returns:
            Dictionary with sync results
        """
        logger.info(f"Starting sync from Google Sheet: {self.sheet_name}")
        
        db = SessionLocal()
        results = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get data from sheet
            sheet_data = self.get_sheet_data()
            
            for row_idx, row in enumerate(sheet_data):
                try:
                    # Parse row
                    student_data = self.parse_student_row(row)
                    
                    if not student_data:
                        results["skipped"] += 1
                        continue
                    
                    # Check if student exists
                    existing = db.query(Student).filter(
                        Student.name == student_data["name"],
                        Student.class_code == student_data["class_code"]
                    ).first()
                    
                    if existing:
                        # Update existing
                        for key, value in student_data.items():
                            if key != "source_id":
                                setattr(existing, key, value)
                        existing.last_modified = datetime.now()
                        results["updated"] += 1
                        logger.debug(f"Updated student: {student_data['name']}")
                    else:
                        # Create new
                        new_student = Student(**student_data)
                        new_student.created_at = datetime.now()
                        db.add(new_student)
                        results["created"] += 1
                        logger.debug(f"Created student: {student_data['name']}")
                    
                except Exception as e:
                    logger.error(f"Error processing row {row_idx}: {e}")
                    results["errors"] += 1
                    continue
            
            # Commit all changes
            db.commit()
            logger.info(f"Sync completed: {results}")
            
            # Log metadata
            self._log_sync_metadata(results)
            
            return results
            
        except Exception as e:
            db.rollback()
            logger.error(f"Sync failed: {e}")
            raise
        finally:
            db.close()
    
    def _log_sync_metadata(self, results: Dict):
        """Log sync results to metadata table"""
        db = SessionLocal()
        try:
            metadata = DataSourceMetadata(
                source_type="google_sheets",
                last_sync=datetime.now(),
                status="success" if results["errors"] == 0 else "partial",
                records_synced=results["created"] + results["updated"],
                error_message="" if results["errors"] == 0 else f"{results['errors']} rows failed"
            )
            db.add(metadata)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging sync metadata: {e}")
        finally:
            db.close()


# Usage in FastAPI endpoint or scheduled task
def sync_google_sheet_handler():
    """Handler for scheduled Google Sheet sync"""
    try:
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Students")
        
        if not sheet_id:
            logger.error("GOOGLE_SHEET_ID not configured")
            return
        
        syncer = GoogleSheetsSync(sheet_id, sheet_name)
        results = syncer.sync()
        
        logger.info(f"Google Sheets sync completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Google Sheets sync failed: {e}")
        raise
