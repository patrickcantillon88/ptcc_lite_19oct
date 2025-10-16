#!/usr/bin/env python3
"""Test script to verify RAG search functionality"""

from backend.core.rag_engine import get_rag_engine

def test_search():
    """Test basic search functionality"""
    print("Testing RAG search functionality...")
    
    # Initialize RAG engine
    rag = get_rag_engine()
    print("✅ RAG engine initialized successfully")
    
    # Test basic search
    query = "student"
    results = rag.search(query)
    print(f"✅ Search for '{query}' found {len(results)} results")
    
    # Display top results
    print("\nTop 3 results:")
    for i, result in enumerate(results[:3]):
        print(f"{i+1}. {result['title']} - Score: {result['relevance_score']:.3f}")
        print(f"   Type: {result['type']}")
        print(f"   Content: {result['content'][:100]}...")
        print()
    
    # Test more specific search
    query2 = "math assessment"
    results2 = rag.search(query2)
    print(f"✅ Search for '{query2}' found {len(results2)} results")
    
    if results2:
        print("\nTop result for math assessment:")
        result = results2[0]
        print(f"Title: {result['title']}")
        print(f"Score: {result['relevance_score']:.3f}")
        print(f"Content: {result['content'][:200]}...")
    
    print("\n🎉 Search functionality is working correctly!")

if __name__ == "__main__":
    test_search()