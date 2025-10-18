# RAG Diagram Image

This directory should contain the RAG workflow diagram image.
The user provided a visual diagram that shows:

1. Additional documents → Encode
2. Embedding model → Index → Vector database  
3. Query → Encode (through embedding model)
4. Similarity search
5. Similar documents
6. Prompt (Query + documents)
7. LLM → Response

The image shows a complete RAG workflow with visual icons and numbered steps in a modern diagram style.

To add the image:
1. Save the image as `rag-diagram.png` in this directory
2. The React component will automatically display it