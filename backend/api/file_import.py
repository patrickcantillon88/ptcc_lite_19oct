"""
File import API endpoints
"""

import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import get_settings, get_data_dir
from ..core.logging_config import get_logger
from ..ingestion.file_parsers import FileParserFactory
from ..ingestion.data_processor import DataProcessor

logger = get_logger("api.import")
router = APIRouter()


class ImportResponse(BaseModel):
    """Response model for file import"""
    success: bool
    message: str
    file_type: str
    processed_data: dict


class ImportResult(BaseModel):
    """Model for import result"""
    file_name: str
    file_type: str
    success: bool
    message: str
    details: dict


@router.post("/file", response_model=ImportResponse)
async def import_file(
    file: UploadFile = File(...),
    file_type: Optional[str] = Form(None),
    auto_detect: bool = Form(True),
    index_for_search: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Import a single file"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    allowed_extensions = ['.xlsx', '.xls', '.pdf', '.docx', '.json']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file
    settings = get_settings()
    temp_dir = os.path.join(get_data_dir(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse file
        parser_factory = FileParserFactory()
        parsed_data = parser_factory.parse_file(temp_file_path)
        
        # Detect file type if not provided
        if auto_detect and not file_type:
            file_type = parser_factory.detect_file_type(temp_file_path)
        elif not file_type:
            file_type = "document"
        
        # Process data
        processor = DataProcessor()
        result = processor.process_file(temp_file_path, parsed_data, file_type)

        # Index for search if requested
        if index_for_search:
            try:
                from ..core.rag_engine import get_rag_engine
                rag_engine = get_rag_engine()

                # Handle different file types for indexing
                if parsed_data.get("file_type") == "json" and "rag_data" in parsed_data:
                    # Special handling for RAG JSON data
                    rag_data = parsed_data["rag_data"]
                    indexed_count = 0

                    for item in rag_data:
                        content = item.get("content", "")
                        metadata = item.get("metadata", {})

                        if content:
                            # Add file info to metadata
                            enhanced_metadata = {
                                **metadata,
                                "file_name": file.filename,
                                "file_type": file_type,
                                "import_date": parsed_data.get("modified_date", ""),
                                "source": "rag_json_import"
                            }

                            rag_engine.index_document(
                                file_path=temp_file_path,
                                content=content,
                                metadata=enhanced_metadata
                            )
                            indexed_count += 1

                    logger.info(f"Indexed {indexed_count} RAG items from JSON file: {file.filename}")

                else:
                    # Standard file indexing
                    text_content = parsed_data.get("full_text", "")
                    if not text_content and parsed_data.get("file_type") == "excel":
                        # For Excel files, create a summary of the data
                        sheets_summary = []
                        for sheet_name, sheet_data in parsed_data.get("sheets", {}).items():
                            if sheet_data.get("row_count", 0) > 0:
                                sheets_summary.append(f"Sheet '{sheet_name}' with {sheet_data['row_count']} rows")
                        text_content = f"Excel file: {file.filename}. Contains: {', '.join(sheets_summary)}"

                    if text_content:
                        rag_engine.index_document(
                            file_path=temp_file_path,
                            content=text_content,
                            metadata={
                                "file_name": file.filename,
                                "file_type": file_type,
                                "import_date": parsed_data.get("modified_date", ""),
                                "source": "file_import"
                            }
                        )

                    logger.info(f"Indexed file for search: {file.filename}")

            except Exception as e:
                logger.warning(f"Failed to index file for search: {e}")
        
        # Move to processed directory
        processed_dir = os.path.join(get_data_dir(), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        processed_file_path = os.path.join(processed_dir, file.filename)
        shutil.move(temp_file_path, processed_file_path)
        
        return ImportResponse(
            success=True,
            message=f"Successfully imported {file.filename}",
            file_type=file_type,
            processed_data=result
        )
        
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        logger.error(f"Error importing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import file: {str(e)}")


@router.post("/directory")
async def import_directory(
    directory_path: str,
    file_pattern: str = "*",
    auto_detect: bool = True,
    index_for_search: bool = True,
    db: Session = Depends(get_db)
):
    """Import all files from a directory"""
    
    # Validate directory
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise HTTPException(status_code=400, detail="Directory not found")
    
    # Find matching files
    import glob
    pattern = os.path.join(directory_path, file_pattern)
    file_paths = glob.glob(pattern)

    # Filter for supported file types
    allowed_extensions = ['.xlsx', '.xls', '.pdf', '.docx', '.json']
    file_paths = [f for f in file_paths if os.path.splitext(f)[1].lower() in allowed_extensions]
    
    if not file_paths:
        return {"message": "No matching files found", "results": []}
    
    # Process files
    parser_factory = FileParserFactory()
    processor = DataProcessor()
    results = []
    
    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            
            # Parse file
            parsed_data = parser_factory.parse_file(file_path)
            
            # Detect file type
            file_type = "document"
            if auto_detect:
                file_type = parser_factory.detect_file_type(file_path)
            
            # Process data
            result = processor.process_file(file_path, parsed_data, file_type)
            
            # Index for search if requested
            if index_for_search:
                try:
                    from ..core.rag_engine import get_rag_engine
                    rag_engine = get_rag_engine()

                    # Handle different file types for indexing
                    if parsed_data.get("file_type") == "json" and "rag_data" in parsed_data:
                        # Special handling for RAG JSON data
                        rag_data = parsed_data["rag_data"]
                        indexed_count = 0

                        for item in rag_data:
                            content = item.get("content", "")
                            metadata = item.get("metadata", {})

                            if content:
                                # Add file info to metadata
                                enhanced_metadata = {
                                    **metadata,
                                    "file_name": file_name,
                                    "file_type": file_type,
                                    "import_date": parsed_data.get("modified_date", ""),
                                    "source": "directory_rag_json_import"
                                }

                                rag_engine.index_document(
                                    file_path=file_path,
                                    content=content,
                                    metadata=enhanced_metadata
                                )
                                indexed_count += 1

                        logger.info(f"Indexed {indexed_count} RAG items from directory JSON file: {file_name}")

                    else:
                        # Standard file indexing
                        text_content = parsed_data.get("full_text", "")
                        if text_content:
                            rag_engine.index_document(
                                file_path=file_path,
                                content=text_content,
                                metadata={
                                    "file_name": file_name,
                                    "file_type": file_type,
                                    "import_date": parsed_data.get("modified_date", ""),
                                    "source": "directory_import"
                                }
                            )

                except Exception as e:
                    logger.warning(f"Failed to index file for search: {file_name} - {e}")
            
            # Move to processed directory
            processed_dir = os.path.join(get_data_dir(), "processed")
            os.makedirs(processed_dir, exist_ok=True)
            
            processed_file_path = os.path.join(processed_dir, file_name)
            if not os.path.exists(processed_file_path):
                shutil.copy2(file_path, processed_file_path)
            
            results.append(ImportResult(
                file_name=file_name,
                file_type=file_type,
                success=True,
                message="Successfully imported",
                details=result
            ))
            
        except Exception as e:
            logger.error(f"Error importing file {file_path}: {e}")
            results.append(ImportResult(
                file_name=os.path.basename(file_path),
                file_type="unknown",
                success=False,
                message=str(e),
                details={}
            ))
    
    successful_imports = sum(1 for r in results if r.success)
    
    return {
        "message": f"Imported {successful_imports} of {len(results)} files",
        "results": results
    }


@router.get("/supported-types")
async def get_supported_file_types():
    """Get list of supported file types"""
    return {
        "supported_extensions": [".xlsx", ".xls", ".pdf", ".docx", ".json"],
        "detected_types": [
            "class_list",
            "assessment",
            "timetable",
            "meeting_minutes",
            "report",
            "communication",
            "document",
            "rag_data"
        ]
    }


@router.get("/status")
async def get_import_status(
    db: Session = Depends(get_db)
):
    """Get status of imported data"""
    try:
        from ..models.database_models import Student, Assessment, Communication
        
        student_count = db.query(Student).count()
        assessment_count = db.query(Assessment).count()
        communication_count = db.query(Communication).count()
        
        # Get processed files count
        processed_dir = os.path.join(get_data_dir(), "processed")
        processed_files = 0
        if os.path.exists(processed_dir):
            processed_files = len([f for f in os.listdir(processed_dir) 
                                 if os.path.isfile(os.path.join(processed_dir, f))])
        
        return {
            "database_status": {
                "students": student_count,
                "assessments": assessment_count,
                "communications": communication_count
            },
            "processed_files": processed_files
        }
        
    except Exception as e:
        logger.error(f"Error getting import status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get import status")