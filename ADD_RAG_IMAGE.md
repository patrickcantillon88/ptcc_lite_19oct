# Adding RAG Diagram Image

## Quick Steps:

1. **Save your RAG diagram image** as `rag-diagram.png`
2. **Place it in**: `frontend/documentation-app/public/rag-diagram.png`
3. **Restart the documentation app** (or it should auto-reload)

## What you'll see:

- **Visual RAG Workflow section** with your colorful diagram showing the complete process
- **ASCII Technical Flow section** with the clean ASCII art underneath
- **Fallback message** if the image isn't found yet

## The image should show:
- Steps 1-7 of the RAG process
- Visual icons (documents, embedding model, database, LLM)
- Numbered workflow steps
- Modern design with colors and connecting arrows

## File structure:
```
frontend/documentation-app/
├── public/
│   └── rag-diagram.png  ← Put your image here
└── src/
    └── components/
        └── RagWorkflow.jsx  ← Already updated
```

The component will automatically display your image once it's in the right location!