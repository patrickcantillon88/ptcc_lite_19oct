#!/usr/bin/env python3
"""
Document Ingestion API for RAG System

Handles uploading, classifying, and embedding documents (PDFs, emails, briefings, policies)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
import io
from pathlib import Path

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..core.rag_engine import get_rag_engine

logger = get_logger("api.documents")
router = APIRouter()


class DocumentType(str, Enum):
    """Document classification types"""
    EMAIL = "email"
    CALENDAR = "calendar"
    POLICY = "policy"
    BRIEFING = "briefing"
    PLANNING = "planning"
    GENERAL = "general"


class TimeContext(str, Enum):
    """Time-based context for retrieval"""
    TODAY = "today"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    THIS_TERM = "this_term"
    ALL_TIME = "all_time"


def classify_document(filename: str, content: str) -> DocumentType:
    """Automatically classify document based on filename and content"""
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    # Email classification
    if any(keyword in filename_lower for keyword in ['email', 'message', 'inbox', 'sent']):
        return DocumentType.EMAIL
    if any(keyword in content_lower[:500] for keyword in ['from:', 'to:', 'subject:', 'dear', 'hi team']):
        return DocumentType.EMAIL
    
    # Calendar classification
    if any(keyword in filename_lower for keyword in ['calendar', 'schedule', 'timetable', 'agenda']):
        return DocumentType.CALENDAR
    if any(keyword in content_lower[:500] for keyword in ['meeting', 'event', 'assembly', 'period']):
        return DocumentType.CALENDAR
    
    # Policy classification
    if any(keyword in filename_lower for keyword in ['policy', 'guideline', 'handbook', 'protocol']):
        return DocumentType.POLICY
    if any(keyword in content_lower[:500] for keyword in ['safeguarding', 'behaviour policy', 'code of conduct']):
        return DocumentType.POLICY
    
    # Briefing classification
    if any(keyword in filename_lower for keyword in ['briefing', 'bulletin', 'memo', 'notice']):
        return DocumentType.BRIEFING
    if any(keyword in content_lower[:500] for keyword in ['weekly briefing', 'daily bulletin', 'announcements']):
        return DocumentType.BRIEFING
    
    # Planning classification
    if any(keyword in filename_lower for keyword in ['plan', 'lesson', 'scheme', 'curriculum']):
        return DocumentType.PLANNING
    
    return DocumentType.GENERAL


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text content from PDF file"""
    if not PyPDF2:
        logger.warning("PyPDF2 not available, cannot extract PDF text")
        return ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None),
    doc_date: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload and index a document into the RAG system
    
    Supports: PDF, TXT, DOCX
    Automatically classifies document type if not provided
    """
    try:
        # Read file content
        content_bytes = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            text_content = extract_text_from_pdf(content_bytes)
        elif file.filename.endswith('.txt'):
            text_content = content_bytes.decode('utf-8')
        elif file.filename.endswith('.docx'):
            # For now, treat as text (could add python-docx library later)
            text_content = content_bytes.decode('utf-8', errors='ignore')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, TXT, or DOCX")
        
        if not text_content or len(text_content) < 10:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from document")
        
        # Classify document type
        if doc_type:
            try:
                document_type = DocumentType(doc_type)
            except ValueError:
                document_type = classify_document(file.filename, text_content)
        else:
            document_type = classify_document(file.filename, text_content)
        
        # Parse document date
        if doc_date:
            try:
                parsed_date = datetime.fromisoformat(doc_date)
            except:
                parsed_date = datetime.now()
        else:
            parsed_date = datetime.now()
        
        # Create metadata
        metadata = {
            "filename": file.filename,
            "doc_type": document_type.value,
            "doc_date": parsed_date.isoformat(),
            "source": source or "manual_upload",
            "description": description or "",
            "uploaded_at": datetime.now().isoformat(),
            "word_count": len(text_content.split())
        }
        
        # Index document in RAG engine
        rag_engine = get_rag_engine()
        rag_engine.index_document(
            file_path=file.filename,
            content=text_content,
            metadata=metadata
        )
        
        logger.info(f"Indexed document: {file.filename} as {document_type.value}")
        
        return {
            "filename": file.filename,
            "doc_type": document_type.value,
            "doc_date": parsed_date.isoformat(),
            "word_count": metadata["word_count"],
            "status": "indexed",
            "message": f"Document successfully indexed as {document_type.value}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/search")
async def search_documents(
    query: str,
    doc_types: Optional[List[str]] = None,
    time_context: Optional[str] = None,
    limit: int = 10
):
    """
    Search documents with time-aware and type-aware filtering
    
    Returns results with citations and source context
    """
    try:
        # Build filters
        filters = {}
        
        if doc_types:
            filters["types"] = ["documents"]  # Search only documents collection
        
        # Time-aware filtering (metadata-based)
        if time_context:
            try:
                context = TimeContext(time_context)
                now = datetime.now()
                
                if context == TimeContext.TODAY:
                    start_date = now.replace(hour=0, minute=0, second=0)
                elif context == TimeContext.THIS_WEEK:
                    start_date = now - timedelta(days=now.weekday())
                elif context == TimeContext.LAST_WEEK:
                    start_date = now - timedelta(days=now.weekday() + 7)
                elif context == TimeContext.THIS_MONTH:
                    start_date = now.replace(day=1, hour=0, minute=0, second=0)
                elif context == TimeContext.THIS_TERM:
                    # Assume term starts in September
                    if now.month >= 9:
                        start_date = now.replace(month=9, day=1)
                    else:
                        start_date = now.replace(year=now.year-1, month=9, day=1)
                else:
                    start_date = None
                
                if start_date:
                    # Note: ChromaDB filtering on dates requires special handling
                    # For now, we'll filter results after retrieval
                    pass
            
            except ValueError:
                pass
        
        # Perform search
        rag_engine = get_rag_engine()
        results = rag_engine.search(query=query, filters=filters, limit=limit * 2)  # Get extra for filtering
        
        # Post-process results: filter by time and extract citations
        filtered_results = []
        
        for result in results:
            metadata = result.get('metadata', {})
            
            # Time filtering
            if time_context and start_date:
                doc_date_str = metadata.get('doc_date')
                if doc_date_str:
                    try:
                        doc_date = datetime.fromisoformat(doc_date_str)
                        if doc_date < start_date:
                            continue  # Skip documents outside time range
                    except:
                        pass
            
            # Doc type filtering
            if doc_types:
                if metadata.get('doc_type') not in doc_types:
                    continue
            
            # Build citation
            citation = {
                "document_id": result.get('id'),
                "filename": metadata.get('filename', 'Unknown'),
                "doc_type": metadata.get('doc_type', 'unknown'),
                "doc_date": metadata.get('doc_date'),
                "source": metadata.get('source', 'unknown'),
                "relevance_score": result.get('relevance_score', 0),
                "excerpt": result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', '')
            }
            
            filtered_results.append(citation)
            
            if len(filtered_results) >= limit:
                break
        
        return {
            "query": query,
            "total_results": len(filtered_results),
            "time_context": time_context,
            "doc_types": doc_types,
            "results": filtered_results
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/list")
async def list_documents():
    """
    List all indexed documents
    """
    try:
        rag_engine = get_rag_engine()
        collection = rag_engine.client.get_collection(rag_engine.collections["documents"])
        
        # Get all documents
        all_docs = collection.get()
        
        documents = []
        for i, doc_id in enumerate(all_docs["ids"]):
            metadata = all_docs["metadatas"][i]
            
            documents.append({
                "id": doc_id,
                "filename": metadata.get("filename", "Unknown"),
                "doc_type": metadata.get("doc_type", "unknown"),
                "doc_date": metadata.get("doc_date"),
                "source": metadata.get("source"),
                "uploaded_at": metadata.get("uploaded_at"),
                "word_count": metadata.get("word_count", 0)
            })
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
        
        return {
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the RAG system
    """
    try:
        rag_engine = get_rag_engine()
        collection = rag_engine.client.get_collection(rag_engine.collections["documents"])
        
        # Delete document
        collection.delete(ids=[document_id])
        
        logger.info(f"Deleted document: {document_id}")
        
        return {
            "document_id": document_id,
            "status": "deleted",
            "message": "Document successfully removed"
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/reindex")
async def reindex_all_documents():
    """
    Rebuild the entire document search index
    """
    try:
        rag_engine = get_rag_engine()
        rag_engine.rebuild_index()
        
        return {
            "status": "success",
            "message": "Search index rebuilt successfully"
        }
        
    except Exception as e:
        logger.error(f"Error reindexing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")
