"""
Search API endpoints
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..core.gemini_client import create_gemini_client_from_config
from ..core.config import get_settings
from functools import lru_cache
import time as _time

logger = get_logger("api.search")
router = APIRouter()


class SearchResult(BaseModel):
    """Model for a single search result"""
    id: str
    type: str
    title: str
    content: str
    source: str
    relevance_score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Response model for search queries"""
    query: str
    results: List[SearchResult]
    total_count: int
    search_time_ms: int


# New in-memory search result cache (query+filters for 60s)
_search_cache = {}
_search_cache_expiry = 60  # seconds

def _make_cache_key(query, filters, limit):
    return f'{query}::{str(filters)}::{limit}'

def _get_from_cache(query, filters, limit):
    key = _make_cache_key(query, filters, limit)
    v = _search_cache.get(key)
    if v and (_time.time() - v['ts'] < _search_cache_expiry):
        return v['data']
    return None

def _set_to_cache(query, filters, limit, value):
    key = _make_cache_key(query, filters, limit)
    _search_cache[key] = { 'data': value, 'ts': _time.time() }

# Patch main search endpoint
@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    filters: Optional[str] = Query(None, description="Comma-separated filters (e.g., students,assessments)"),
    db: Session = Depends(get_db)
):
    """Search across all data using AI-enhanced semantic search"""
    try:
        import time
        start_time = time.time()

        # Parse filters
        filter_types = []
        if filters:
            filters_str = str(filters) if hasattr(filters, '__str__') else filters
            filter_types = [f.strip().lower() for f in filters_str.split(",")]

        # Caching: skip DB/rag_engine if cached
        cached = _get_from_cache(q, filter_types, limit)
        if cached:
            results, total_count, elapsed = cached
            return SearchResponse(
                query=q, results=results, total_count=total_count, search_time_ms=int(elapsed*1000))

        # Initialize Gemini client for AI-enhanced search
        settings = get_settings()
        gemini_client = create_gemini_client_from_config(settings)

        # Analyze query intent using Gemini
        query_analysis = None
        if gemini_client.is_available():
            query_analysis = gemini_client.analyze_query_intent(q)
            if query_analysis:
                logger.info(f"Query analysis: {query_analysis}")

        # Use RAG engine for semantic search
        from ..core.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        search_filters = {}
        if filter_types:
            search_filters["types"] = filter_types

        search_query = q
        if query_analysis and "expansions" in query_analysis:
            expansions = query_analysis.get("expansions", [])
            if expansions:
                search_query = f"{q} {' '.join(expansions[:2])}"  # Add up to 2 expansions

        rag_results = rag_engine.search(search_query, search_filters, limit * 2)
        results = []
        for result in rag_results:
            results.append(SearchResult(
                id=result["id"],
                type=result["type"],
                title=result["title"],
                content=result["content"],
                source=result["source"],
                relevance_score=result["relevance_score"],
                metadata=result["metadata"]
            ))
        # Gemini re-ranking
        if gemini_client.is_available() and len(results) > 1:
            try:
                result_dicts = [
                    {
                        "id": r.id,
                        "type": r.type,
                        "title": r.title,
                        "content": r.content,
                        "source": r.source,
                        "relevance_score": r.relevance_score,
                        "metadata": r.metadata
                    }
                    for r in results
                ]
                ranked = gemini_client.rank_documents(query=q, documents=result_dicts)
                # Assume rank_documents returns IDs in order of most relevant
                if ranked and isinstance(ranked, list):
                    id_rank = {id_: i for i, id_ in enumerate(ranked)}
                    results.sort(key=lambda x: id_rank.get(x.id, len(id_rank)))
            except Exception as e:
                logger.warning(f"Gemini ranking failed: {e}")
        total_count = len(results)
        elapsed = time.time() - start_time
        results = results[offset:offset+limit]
        # Set cache for this response
        _set_to_cache(q, filter_types, limit, (results, total_count, elapsed))
        return SearchResponse(
            query=q,
            results=results,
            total_count=total_count,
            search_time_ms=int(elapsed*1000)
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/students")
async def search_students(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search students by name or class"""
    try:
        from ..models.database_models import Student
        
        students = db.query(Student).filter(
            Student.name.contains(q)
        ).limit(limit).all()
        
        results = []
        for student in students:
            results.append({
                "id": f"student-{student.id}",
                "name": student.name,
                "class_code": student.class_code,
                "year_group": student.year_group,
                "campus": student.campus,
                "support_level": student.support_level,
                "support_notes": student.support_notes
            })
        
        return {"query": q, "results": results, "total_count": len(results)}
        
    except Exception as e:
        logger.error(f"Error searching students: {e}")
        raise HTTPException(status_code=500, detail="Student search failed")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get search suggestions for autocomplete"""
    try:
        from ..models.database_models import Student
        
        # Get student name suggestions
        students = db.query(Student).filter(
            Student.name.contains(q)
        ).limit(limit).all()
        
        suggestions = []
        for student in students:
            suggestions.append({
                "text": student.name,
                "type": "student",
                "description": f"{student.class_code} - Year {student.year_group}"
            })
        
        # TODO: Add suggestions for other entities when RAG is implemented
        
        return {"query": q, "suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


def _search_students(db: Session, query: str, limit: int) -> List[SearchResult]:
    """Search students by name or class"""
    from ..models.database_models import Student
    
    students = db.query(Student).filter(
        Student.name.contains(query) | 
        Student.class_code.contains(query)
    ).limit(limit).all()
    
    results = []
    for student in students:
        # Simple relevance scoring
        relevance = 1.0
        if query.lower() in student.name.lower():
            relevance += 0.5
        if query.lower() in student.class_code.lower():
            relevance += 0.3
        
        results.append(SearchResult(
            id=f"student-{student.id}",
            type="student",
            title=student.name,
            content=f"Student in {student.class_code}, Year {student.year_group}, Campus {student.campus}",
            source="students",
            relevance_score=relevance,
            metadata={
                "class_code": student.class_code,
                "year_group": student.year_group,
                "campus": student.campus,
                "support_level": student.support_level
            }
        ))
    
    return results


@router.post("/index/rebuild")
async def rebuild_search_index(
    db: Session = Depends(get_db)
):
    """Rebuild the search index"""
    try:
        from ..core.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        # Rebuild index
        rag_engine.rebuild_index()
        
        return {"message": "Search index rebuilt successfully"}
        
    except Exception as e:
        logger.error(f"Error rebuilding search index: {e}")
        raise HTTPException(status_code=500, detail="Failed to rebuild search index")


@router.get("/index/status")
async def get_index_status(
    db: Session = Depends(get_db)
):
    """Get the status of the search index"""
    try:
        from ..core.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        # Get collection information
        collections_info = {}
        for collection_name in rag_engine.collections.values():
            try:
                collection = rag_engine.client.get_collection(collection_name)
                count = collection.count()
                collections_info[collection_name] = {
                    "name": collection_name,
                    "count": count,
                    "status": "ready" if count > 0 else "empty"
                }
            except Exception as e:
                collections_info[collection_name] = {
                    "name": collection_name,
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "ready",
            "collections": collections_info,
            "total_items": sum(info["count"] for info in collections_info.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting index status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get index status")


def _search_logs(db: Session, query: str, limit: int) -> List[SearchResult]:
    """Search quick logs by content"""
    from ..models.database_models import QuickLog, Student
    
    logs = db.query(QuickLog).join(Student).filter(
        QuickLog.note.contains(query) |
        QuickLog.category.contains(query) |
        Student.name.contains(query)
    ).limit(limit).all()
    
    results = []
    for log in logs:
        # Simple relevance scoring
        relevance = 1.0
        if query.lower() in (log.note or "").lower():
            relevance += 0.5
        if query.lower() in log.category.lower():
            relevance += 0.3
        
        results.append(SearchResult(
            id=f"log-{log.id}",
            type="log",
            title=f"{log.log_type} log for {log.student.name}",
            content=log.note or log.category,
            source="quick_logs",
            relevance_score=relevance,
            metadata={
                "student_id": log.student_id,
                "student_name": log.student.name,
                "class_code": log.class_code,
                "log_type": log.log_type,
                "category": log.category,
                "timestamp": log.timestamp.isoformat()
            }
        ))
    
    return results


def _search_assessments(db: Session, query: str, limit: int) -> List[SearchResult]:
    """Search assessments by subject or topic"""
    from ..models.database_models import Assessment, Student
    
    assessments = db.query(Assessment).join(Student).filter(
        Assessment.subject.contains(query) |
        Assessment.topic.contains(query) |
        Assessment.assessment_type.contains(query) |
        Student.name.contains(query)
    ).limit(limit).all()
    
    results = []
    for assessment in assessments:
        # Simple relevance scoring
        relevance = 1.0
        if query.lower() in (assessment.subject or "").lower():
            relevance += 0.5
        if query.lower() in (assessment.topic or "").lower():
            relevance += 0.3
        
        results.append(SearchResult(
            id=f"assessment-{assessment.id}",
            type="assessment",
            title=f"{assessment.assessment_type}: {assessment.subject}",
            content=f"Score: {assessment.score}/{assessment.max_score} ({assessment.percentage}%)",
            source="assessments",
            relevance_score=relevance,
            metadata={
                "student_id": assessment.student_id,
                "student_name": assessment.student.name,
                "assessment_type": assessment.assessment_type,
                "subject": assessment.subject,
                "topic": assessment.topic,
                "score": assessment.score,
                "percentage": assessment.percentage,
                "date": assessment.date.isoformat()
            }
        ))
    
    return results

def search_all(query: str, limit: int = 10, db: Session = None) -> Dict[str, Any]:
    """Search across all data sources"""
    try:
        all_results = []
        
        # Search students
        if db:
            student_results = _search_students(db, query, limit)
            all_results.extend(student_results)
            
            # Search logs
            log_results = _search_logs(db, query, limit)
            all_results.extend(log_results)
            
            # Search assessments
            assessment_results = _search_assessments(db, query, limit)
            all_results.extend(assessment_results)
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Convert to dict format
        dict_results = []
        for result in all_results[:limit]:
            dict_results.append({
                "id": result.id,
                "type": result.type,
                "title": result.title,
                "content": result.content,
                "source": result.source,
                "relevance_score": result.relevance_score,
                "metadata": result.metadata
            })
        
        return {
            "results": dict_results,
            "total_count": len(dict_results)
        }
    except Exception as e:
        logger.error(f"Error in search_all: {e}")
        return {"results": [], "total_count": 0}