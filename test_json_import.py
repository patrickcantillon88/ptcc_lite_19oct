#!/usr/bin/env python3
"""Test script to import RAG JSON data directly"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.ingestion.file_parsers import FileParserFactory
from backend.core.rag_engine import get_rag_engine
from backend.core.logging_config import get_logger

logger = get_logger("test_json_import")

def test_json_import():
    """Test importing RAG JSON data"""
    json_file = "Example docs/rag_data.json"
    
    print(f"Testing JSON import for: {json_file}")
    
    # Parse JSON file
    parser_factory = FileParserFactory()
    print("Parsing JSON file...")
    parsed_data = parser_factory.parse_file(json_file)
    
    print(f"✅ Parsed successfully!")
    print(f"   File type: {parsed_data['file_type']}")
    print(f"   Items: {parsed_data.get('item_count', 0)}")
    
    # Index into RAG
    print("\nIndexing into RAG engine...")
    rag_engine = get_rag_engine()
    
    if "rag_data" in parsed_data:
        rag_data = parsed_data["rag_data"]
        indexed_count = 0
        
        for i, item in enumerate(rag_data):
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            
            if content:
                enhanced_metadata = {
                    **metadata,
                    "file_name": "rag_data.json",
                    "file_type": "rag_data",
                    "source": "json_import_test"
                }
                
                rag_engine.index_document(
                    file_path=json_file,
                    content=content,
                    metadata=enhanced_metadata
                )
                indexed_count += 1
                
                if (i + 1) % 500 == 0:
                    print(f"   Indexed {i + 1} items...")
        
        print(f"✅ Indexed {indexed_count} RAG items!")
        
        # Test search
        print("\nTesting search...")
        results = rag_engine.search("Year 1 curriculum")
        print(f"✅ Search found {len(results)} results")
        
        if results:
            print("\nTop 3 results:")
            for i, result in enumerate(results[:3]):
                print(f"{i+1}. {result['title'][:50]}... - Score: {result['relevance_score']:.3f}")
                print(f"   Source: {result['metadata'].get('source', 'N/A')}")
    
    print("\n🎉 JSON import test completed successfully!")

if __name__ == "__main__":
    test_json_import()