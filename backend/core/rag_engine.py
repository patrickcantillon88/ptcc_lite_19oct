"""
RAG (Retrieval-Augmented Generation) search engine
"""

import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .database import SessionLocal
from .config import get_settings, get_chroma_path
from .logging_config import get_logger

logger = get_logger("rag_engine")


class RAGEngine:
    """RAG search engine for semantic search across all data"""
    
    def __init__(self):
        self.settings = get_settings()
        self.chroma_path = get_chroma_path()
        
        # Ensure ChromaDB directory exists
        os.makedirs(self.chroma_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize sentence transformer model
        model_name = "all-MiniLM-L6-v2"  # Lightweight, good performance
        self.embedding_model = SentenceTransformer(model_name)
        
        # Collection names
        self.collections = {
            "students": "student_information",
            "logs": "quick_logs",
            "assessments": "assessments",
            "communications": "communications",
            "documents": "documents"
        }
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize ChromaDB collections"""
        for collection_name in self.collections.values():
            try:
                # Try to get existing collection
                self.client.get_collection(name=collection_name)
                logger.info(f"Collection '{collection_name}' already exists")
            except Exception:
                # Create new collection if it doesn't exist
                self.client.create_collection(
                    name=collection_name,
                    metadata={"description": f"Collection for {collection_name}"}
                )
                logger.info(f"Created collection '{collection_name}'")
    
    def index_database_data(self):
        """Index all database data into ChromaDB"""
        logger.info("Starting database indexing...")
        
        db = SessionLocal()
        try:
            # Index students
            self._index_students(db)
            
            # Index quick logs
            self._index_quick_logs(db)
            
            # Index assessments
            self._index_assessments(db)
            
            # Index communications
            self._index_communications(db)
            
            logger.info("Database indexing completed")
            
        finally:
            db.close()
    
    def _index_students(self, db):
        """Index student data"""
        from ..models.database_models import Student
        
        collection = self.client.get_collection(self.collections["students"])
        
        # Clear existing data
        try:
            collection.delete(where={})
        except Exception:
            # If empty where clause fails, try to delete all documents
            try:
                # Get all IDs and delete them individually
                all_data = collection.get()
                if all_data["ids"]:
                    collection.delete(ids=all_data["ids"])
            except Exception:
                # If that fails, just continue (collection might be empty)
                pass
        
        students = db.query(Student).all()
        
        documents = []
        metadatas = []
        ids = []
        
        for student in students:
            # Create searchable text
            text = f"{student.name} is a student in class {student.class_code}, year {student.year_group} at campus {student.campus}."
            
            if student.support_notes:
                text += f" Support notes: {student.support_notes}"
            
            if student.house:
                text += f" House: {student.house}"
            
            documents.append(text)
            
            metadatas.append({
                "student_id": student.id,
                "name": student.name,
                "class_code": student.class_code,
                "year_group": student.year_group,
                "campus": student.campus,
                "support_level": student.support_level,
                "type": "student"
            })
            
            ids.append(f"student_{student.id}")
        
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} students")
    
    def _index_quick_logs(self, db):
        """Index quick log data"""
        from ..models.database_models import QuickLog, Student
        
        collection = self.client.get_collection(self.collections["logs"])
        
        # Clear existing data
        try:
            collection.delete(where={})
        except Exception:
            # If empty where clause fails, try to delete all documents
            try:
                # Get all IDs and delete them individually
                all_data = collection.get()
                if all_data["ids"]:
                    collection.delete(ids=all_data["ids"])
            except Exception:
                # If that fails, just continue (collection might be empty)
                pass
        
        logs = db.query(QuickLog).join(Student).all()
        
        documents = []
        metadatas = []
        ids = []
        
        for log in logs:
            # Create searchable text
            text = f"{log.log_type} log for {log.student.name} in class {log.class_code}. Category: {log.category}."
            
            if log.note:
                text += f" Note: {log.note}"
            
            if log.points != 0:
                text += f" Points: {log.points}"
            
            text += f" Date: {log.timestamp.strftime('%Y-%m-%d')}"
            
            documents.append(text)
            
            metadatas.append({
                "log_id": log.id,
                "student_id": log.student_id,
                "student_name": log.student.name,
                "class_code": log.class_code,
                "log_type": log.log_type,
                "category": log.category,
                "points": log.points,
                "timestamp": log.timestamp.isoformat(),
                "type": "log"
            })
            
            ids.append(f"log_{log.id}")
        
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} quick logs")
    
    def _index_assessments(self, db):
        """Index assessment data"""
        from ..models.database_models import Assessment, Student
        
        collection = self.client.get_collection(self.collections["assessments"])
        
        # Clear existing data
        try:
            collection.delete(where={})
        except Exception:
            # If empty where clause fails, try to delete all documents
            try:
                # Get all IDs and delete them individually
                all_data = collection.get()
                if all_data["ids"]:
                    collection.delete(ids=all_data["ids"])
            except Exception:
                # If that fails, just continue (collection might be empty)
                pass
        
        assessments = db.query(Assessment).join(Student).all()
        
        documents = []
        metadatas = []
        ids = []
        
        for assessment in assessments:
            # Create searchable text
            text = f"{assessment.assessment_type} assessment for {assessment.student.name} in {assessment.subject}."
            
            if assessment.topic:
                text += f" Topic: {assessment.topic}."
            
            text += f" Score: {assessment.score}/{assessment.max_score} ({assessment.percentage:.1f}%)."
            text += f" Date: {assessment.date.strftime('%Y-%m-%d')}"
            
            documents.append(text)
            
            metadatas.append({
                "assessment_id": assessment.id,
                "student_id": assessment.student_id,
                "student_name": assessment.student.name,
                "assessment_type": assessment.assessment_type,
                "subject": assessment.subject,
                "topic": assessment.topic or "",
                "score": assessment.score,
                "max_score": assessment.max_score,
                "percentage": assessment.percentage,
                "date": assessment.date.isoformat(),
                "type": "assessment"
            })
            
            ids.append(f"assessment_{assessment.id}")
        
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} assessments")
    
    def _index_communications(self, db):
        """Index communication data"""
        from ..models.database_models import Communication
        
        collection = self.client.get_collection(self.collections["communications"])
        
        # Clear existing data
        try:
            collection.delete(where={})
        except Exception:
            # If empty where clause fails, try to delete all documents
            try:
                # Get all IDs and delete them individually
                all_data = collection.get()
                if all_data["ids"]:
                    collection.delete(ids=all_data["ids"])
            except Exception:
                # If that fails, just continue (collection might be empty)
                pass
        
        communications = db.query(Communication).all()
        
        documents = []
        metadatas = []
        ids = []
        
        for comm in communications:
            # Create searchable text
            text = f"Communication from {comm.sender}: {comm.subject}."
            
            if comm.content:
                text += f" Content: {comm.content}"
            
            text += f" Category: {comm.category}. Campus: {comm.campus or 'Both'}."
            text += f" Date: {comm.received_date.strftime('%Y-%m-%d')}"
            
            documents.append(text)
            
            metadatas.append({
                "comm_id": comm.id,
                "sender": comm.sender,
                "subject": comm.subject,
                "category": comm.category,
                "campus": comm.campus or "",
                "source": comm.source,
                "received_date": comm.received_date.isoformat(),
                "action_required": comm.action_required,
                "read": comm.read,
                "type": "communication"
            })
            
            ids.append(f"comm_{comm.id}")
        
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} communications")
    
    def index_document(self, file_path: str, content: str, metadata: Dict[str, Any]):
        """Index a document file"""
        collection = self.client.get_collection(self.collections["documents"])
        
        # Create a unique ID based on file path
        doc_id = f"doc_{hash(file_path)}"
        
        # Add document to collection
        collection.add(
            documents=[content],
            metadatas=[{
                "file_path": file_path,
                **metadata,
                "type": "document"
            }],
            ids=[doc_id]
        )
        
        logger.info(f"Indexed document: {file_path}")
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search across all indexed data, with parallel ChromaDB collection queries when possible."""
        results = []
        collections_to_search = list(self.collections.values())
        if filters and "types" in filters:
            type_mapping = {
                "students": "student_information",
                "logs": "quick_logs",
                "assessments": "assessments",
                "communications": "communications",
                "documents": "documents"
            }
            collections_to_search = [type_mapping[t] for t in filters["types"] if t in type_mapping]

        async def search_one(collection_name):
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._search_collection, collection_name, query, filters, limit)

        def sequential():
            seq_results = []
            for c in collections_to_search:
                seq_results.extend(self._search_collection(c, query, filters, limit))
            return seq_results

        try:
            # Try parallel execution with asyncio if possible
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                tasks = [search_one(c) for c in collections_to_search]
                gathered = loop.run_until_complete(asyncio.gather(*tasks))
                # Flatten
                for chunk in gathered:
                    results.extend(chunk)
            else:
                # Not in an event loop, use plain sequential
                results = sequential()
        except Exception as e:
            logger.warning(f"Async search failed or not available, falling back: {e}")
            results = sequential()

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def _search_collection(self, collection_name, query, filters, limit):
        # Function unchanged from the old for-loop's body for one collection
        try:
            collection = self.client.get_collection(collection_name)
            where_filter = None
            if filters:
                temp_filter = {}
                for key, value in filters.items():
                    if key != "types":
                        temp_filter[key] = value
                if temp_filter:
                    where_filter = temp_filter

            # Prepare search params
            query_params = {
                "query_texts": [query],
                "n_results": limit
            }
            if where_filter is not None:
                query_params["where"] = where_filter
            search_results = collection.query(**query_params)
            chunk = []
            for i, doc in enumerate(search_results["documents"][0]):
                metadata = search_results["metadatas"][0][i]
                distance = search_results["distances"][0][i]
                relevance_score = 1.0 - min(distance, 1.0)
                chunk.append({
                    "id": metadata.get("id", f"{collection_name}_{i}"),
                    "type": metadata.get("type", "unknown"),
                    "title": self._extract_title(metadata, doc),
                    "content": doc,
                    "source": collection_name,
                    "relevance_score": relevance_score,
                    "metadata": metadata
                })
            return chunk
        except Exception as e:
            logger.warning(f"Error searching collection {collection_name}: {e}")
            return []
    
    def _extract_title(self, metadata: Dict[str, Any], content: str) -> str:
        """Extract a meaningful title from metadata and content"""
        type_ = metadata.get("type", "unknown")
        
        if type_ == "student":
            return metadata.get("name", "Student")
        elif type_ == "log":
            return f"{metadata.get('log_type', 'Log')} for {metadata.get('student_name', 'Student')}"
        elif type_ == "assessment":
            return f"{metadata.get('assessment_type', 'Assessment')}: {metadata.get('subject', 'Subject')}"
        elif type_ == "communication":
            return metadata.get("subject", "Communication")
        elif type_ == "document":
            return os.path.basename(metadata.get("file_path", "Document"))
        else:
            # Use first 50 characters of content as title
            return content[:50] + "..." if len(content) > 50 else content
    
    def get_similar_items(self, item_id: str, item_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find items similar to a specific item"""
        try:
            # Get the appropriate collection
            collection_name = self.collections.get(item_type)
            if not collection_name:
                return []
            
            collection = self.client.get_collection(collection_name)
            
            # Get the item
            item_data = collection.get(ids=[item_id])
            if not item_data["documents"]:
                return []
            
            # Use the item's content to find similar items
            query_text = item_data["documents"][0]
            
            # Search for similar items (excluding the original)
            similar_results = collection.query(
                query_texts=[query_text],
                n_results=limit + 1,  # Get one extra to exclude the original
                where={"id": {"$ne": item_id}}  # Exclude the original item
            )
            
            results = []
            for i, doc in enumerate(similar_results["documents"][0]):
                metadata = similar_results["metadatas"][0][i]
                distance = similar_results["distances"][0][i]
                
                # Convert distance to relevance score
                relevance_score = 1.0 - min(distance, 1.0)
                
                results.append({
                    "id": metadata.get("id", f"{collection_name}_{i}"),
                    "type": metadata.get("type", "unknown"),
                    "title": self._extract_title(metadata, doc),
                    "content": doc,
                    "source": collection_name,
                    "relevance_score": relevance_score,
                    "metadata": metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar items: {e}")
            return []
    
    def rebuild_index(self):
        """Rebuild the entire search index"""
        logger.info("Rebuilding search index...")
        
        # Delete all collections
        for collection_name in self.collections.values():
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass
        
        # Reinitialize collections
        self._init_collections()
        
        # Reindex all data
        self.index_database_data()
        
        logger.info("Search index rebuilt successfully")


# Global RAG engine instance
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get the global RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine