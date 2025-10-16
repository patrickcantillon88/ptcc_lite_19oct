"""
Data processor for importing parsed data into the database
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from pathlib import Path

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..core.logging_config import get_logger
from ..models.database_models import (
    Student, Schedule, ClassRoster, QuickLog, Assessment,
    Reminder, DutyRota, Communication
)

logger = get_logger("data_processor")


class DataProcessor:
    """Process parsed data and import into database"""
    
    def __init__(self):
        self.processors = {
            "class_list": self._process_class_list,
            "assessment": self._process_assessment,
            "timetable": self._process_timetable,
            "meeting_minutes": self._process_meeting_minutes,
            "report": self._process_report,
            "communication": self._process_communication,
            "document": self._process_document
        }
    
    def process_file(self, file_path: str, parsed_data: Dict[str, Any], file_type: str = None) -> Dict[str, Any]:
        """Process a parsed file and import data into database"""
        if not file_type:
            file_type = "document"
        
        # Get the appropriate processor
        processor = self.processors.get(file_type, self._process_document)
        
        db = SessionLocal()
        try:
            result = processor(db, file_path, parsed_data, file_type)
            db.commit()
            
            logger.info(f"Successfully processed {file_type} file: {file_path}")
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing {file_type} file {file_path}: {e}")
            raise
        finally:
            db.close()
    
    def _process_class_list(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process class list data"""
        result = {
            "file_type": file_type,
            "students_added": 0,
            "students_updated": 0,
            "errors": []
        }
        
        try:
            # Extract data from Excel sheets
            if parsed_data.get("file_type") == "excel":
                for sheet_name, sheet_data in parsed_data.get("sheets", {}).items():
                    if sheet_data.get("row_count", 0) == 0:
                        continue
                    
                    # Find name column
                    columns = sheet_data["columns"]
                    name_col = self._find_column(columns, ["name", "student", "pupil", "full name"])
                    class_col = self._find_column(columns, ["class", "form", "group"])
                    year_col = self._find_column(columns, ["year", "grade", "level"])
                    
                    if not name_col:
                        result["errors"].append(f"Could not find name column in sheet '{sheet_name}'")
                        continue
                    
                    # Process each row
                    for row_num, row in enumerate(sheet_data["data"], 2):  # Start at 2 for Excel row numbers
                        try:
                            name = row.get(name_col, "").strip()
                            if not name:
                                continue
                            
                            # Extract other fields
                            class_code = row.get(class_col, "").strip() if class_col else ""
                            year_group = row.get(year_col, "").strip() if year_col else ""
                            
                            # Default values
                            if not class_code and name:
                                # Try to extract from name if format includes class
                                parts = name.split()
                                if len(parts) >= 2 and parts[-1].isdigit():
                                    class_code = parts[-1]
                                    name = " ".join(parts[:-1])
                            
                            if not year_group and class_code:
                                year_group = class_code[0] if class_code[0].isdigit() else ""
                            
                            # Check if student already exists
                            existing_student = db.query(Student).filter(Student.name == name).first()
                            
                            if existing_student:
                                # Update existing student
                                if class_code:
                                    existing_student.class_code = class_code
                                if year_group:
                                    existing_student.year_group = year_group
                                existing_student.last_updated = datetime.utcnow()
                                result["students_updated"] += 1
                            else:
                                # Create new student
                                student = Student(
                                    name=name,
                                    class_code=class_code or "Unknown",
                                    year_group=year_group or "Unknown",
                                    campus="A",  # Default campus
                                    support_level=0  # Default support level
                                )
                                db.add(student)
                                result["students_added"] += 1
                            
                        except Exception as e:
                            result["errors"].append(f"Error processing row {row_num} in sheet '{sheet_name}': {e}")
            
        except Exception as e:
            result["errors"].append(f"Error processing class list: {e}")
        
        return result
    
    def _process_assessment(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process assessment data"""
        result = {
            "file_type": file_type,
            "assessments_added": 0,
            "students_found": 0,
            "errors": []
        }
        
        try:
            if parsed_data.get("file_type") == "excel":
                for sheet_name, sheet_data in parsed_data.get("sheets", {}).items():
                    if sheet_data.get("row_count", 0) == 0:
                        continue
                    
                    columns = sheet_data["columns"]
                    name_col = self._find_column(columns, ["name", "student", "pupil"])
                    score_col = self._find_column(columns, ["score", "mark", "grade", "result"])
                    max_score_col = self._find_column(columns, ["max", "total", "out of", "possible"])
                    subject_col = self._find_column(columns, ["subject", "test", "assessment", "exam"])
                    
                    if not name_col or not score_col:
                        result["errors"].append(f"Could not find required columns in sheet '{sheet_name}'")
                        continue
                    
                    # Get subject from sheet name if not found in columns
                    subject = sheet_name if not subject_col else None
                    
                    # Process each row
                    for row_num, row in enumerate(sheet_data["data"], 2):
                        try:
                            name = row.get(name_col, "").strip()
                            if not name:
                                continue
                            
                            # Find student
                            student = db.query(Student).filter(Student.name == name).first()
                            if not student:
                                # Try fuzzy matching
                                student = db.query(Student).filter(Student.name.contains(name.split()[0])).first()
                            
                            if not student:
                                result["errors"].append(f"Student not found: {name} (row {row_num})")
                                continue
                            
                            result["students_found"] += 1
                            
                            # Extract score data
                            score = self._parse_number(row.get(score_col, 0))
                            max_score = self._parse_number(row.get(max_score_col, 100)) if max_score_col else 100
                            subject_val = row.get(subject_col, "").strip() if subject_col else subject or "Unknown"
                            
                            # Calculate percentage
                            percentage = (score / max_score * 100) if max_score > 0 else 0
                            
                            # Create assessment
                            assessment = Assessment(
                                student_id=student.id,
                                assessment_type="Imported Assessment",
                                subject=subject_val,
                                topic=f"Imported from {os.path.basename(file_path)}",
                                score=score,
                                max_score=max_score,
                                percentage=percentage,
                                date=date.today(),
                                source=os.path.basename(file_path)
                            )
                            
                            db.add(assessment)
                            result["assessments_added"] += 1
                            
                        except Exception as e:
                            result["errors"].append(f"Error processing row {row_num} in sheet '{sheet_name}': {e}")
            
        except Exception as e:
            result["errors"].append(f"Error processing assessment data: {e}")
        
        return result
    
    def _process_timetable(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process timetable data"""
        result = {
            "file_type": file_type,
            "schedule_entries_added": 0,
            "errors": []
        }
        
        try:
            if parsed_data.get("file_type") == "excel":
                for sheet_name, sheet_data in parsed_data.get("sheets", {}).items():
                    if sheet_data.get("row_count", 0) == 0:
                        continue
                    
                    # This is a simplified implementation
                    # A real implementation would need to handle complex timetable formats
                    result["errors"].append("Timetable processing requires manual review and formatting")
            
        except Exception as e:
            result["errors"].append(f"Error processing timetable: {e}")
        
        return result
    
    def _process_meeting_minutes(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process meeting minutes"""
        result = {
            "file_type": file_type,
            "communications_added": 0,
            "errors": []
        }
        
        try:
            # Extract text content
            text = parsed_data.get("full_text", "")
            if not text:
                result["errors"].append("No text content found in document")
                return result
            
            # Create communication entry
            communication = Communication(
                source="document",
                subject=f"Meeting Minutes: {os.path.basename(file_path)}",
                sender="Meeting",
                content=text[:2000],  # Limit content length
                category="fyi",
                received_date=datetime.now(),
                action_required=False,
                read=False
            )
            
            db.add(communication)
            result["communications_added"] = 1
            
        except Exception as e:
            result["errors"].append(f"Error processing meeting minutes: {e}")
        
        return result
    
    def _process_report(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process reports"""
        result = {
            "file_type": file_type,
            "communications_added": 0,
            "errors": []
        }
        
        try:
            # Extract text content
            text = parsed_data.get("full_text", "")
            if not text:
                result["errors"].append("No text content found in document")
                return result
            
            # Create communication entry
            communication = Communication(
                source="document",
                subject=f"Report: {os.path.basename(file_path)}",
                sender="System",
                content=text[:2000],  # Limit content length
                category="fyi",
                received_date=datetime.now(),
                action_required=False,
                read=False
            )
            
            db.add(communication)
            result["communications_added"] = 1
            
        except Exception as e:
            result["errors"].append(f"Error processing report: {e}")
        
        return result
    
    def _process_communication(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process communications"""
        result = {
            "file_type": file_type,
            "communications_added": 0,
            "errors": []
        }
        
        try:
            # Extract text content
            text = parsed_data.get("full_text", "")
            if not text:
                result["errors"].append("No text content found in document")
                return result
            
            # Determine if urgent based on content
            text_lower = text.lower()
            is_urgent = any(keyword in text_lower for keyword in ["urgent", "important", "immediate", "asap"])
            
            # Create communication entry
            communication = Communication(
                source="document",
                subject=os.path.basename(file_path).replace('.pdf', '').replace('.docx', ''),
                sender="System",
                content=text[:2000],  # Limit content length
                category="urgent" if is_urgent else "fyi",
                received_date=datetime.now(),
                action_required=is_urgent,
                read=False
            )
            
            db.add(communication)
            result["communications_added"] = 1
            
        except Exception as e:
            result["errors"].append(f"Error processing communication: {e}")
        
        return result
    
    def _process_document(self, db: Session, file_path: str, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process generic document"""
        result = {
            "file_type": file_type,
            "communications_added": 0,
            "errors": []
        }
        
        try:
            # Extract text content
            text = parsed_data.get("full_text", "")
            if not text:
                result["errors"].append("No text content found in document")
                return result
            
            # Create communication entry for searchable content
            communication = Communication(
                source="document",
                subject=f"Document: {os.path.basename(file_path)}",
                sender="System",
                content=text[:2000],  # Limit content length
                category="fyi",
                received_date=datetime.now(),
                action_required=False,
                read=False
            )
            
            db.add(communication)
            result["communications_added"] = 1
            
        except Exception as e:
            result["errors"].append(f"Error processing document: {e}")
        
        return result
    
    def _find_column(self, columns: List[str], possible_names: List[str]) -> Optional[str]:
        """Find a column from a list of possible names"""
        columns_lower = [col.lower() for col in columns]
        
        for name in possible_names:
            for i, col_lower in enumerate(columns_lower):
                if name.lower() in col_lower:
                    return columns[i]
        
        return None
    
    def _parse_number(self, value: Any) -> float:
        """Parse a number from various formats"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common formatting
            cleaned = value.replace("%", "").replace(",", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                pass
        
        return 0.0