from fastapi import FastAPI, UploadFile, Form, HTTPException
from .database import Base, engine, SessionLocal
from .models import Document
from .utils import extract_text_from_file
from .chunking import chunk_by_sentences, chunk_by_fixed_length
from .embeddings import init_qdrant, store_embeddings
from .operation import query_chatbot

# Initialize with error handling
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization error: {str(e)}")
    raise

try:
    init_qdrant()
except Exception as e:
    print(f"Qdrant initialization error: {str(e)}")
    raise

app = FastAPI()

# Existing /upload endpoint with error handling
@app.post("/upload")
async def upload_document(file: UploadFile, chunk_strategy: str = Form(...)):
    db = None
    try:
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="File has no filename")
        
        # Validate chunk strategy
        if chunk_strategy not in ["sentences", "fixed"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid chunk_strategy. Must be 'sentences' or 'fixed'"
            )
        
        # Extract text from file
        try:
            text = extract_text_from_file(file)
            if not text or not text.strip():
                raise HTTPException(status_code=400, detail="Extracted text is empty")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=422, 
                detail=f"Failed to extract text from file: {str(e)}"
            )

        # Chunk the text
        try:
            if chunk_strategy == "sentences":
                chunks = chunk_by_sentences(text)
            else:
                chunks = chunk_by_fixed_length(text)
            
            if not chunks:
                raise HTTPException(status_code=400, detail="No chunks created from text")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to chunk text: {str(e)}"
            )

        # Save metadata to Postgres
        db = SessionLocal()
        try:
            doc = Document(
                filename=file.filename, 
                chunk_strategy=chunk_strategy, 
                content=text
            )
            db.add(doc)
            db.commit()
        except Exception as e:
            if db:
                db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Database error: {str(e)}"
            )

        # Store embeddings in Qdrant
        try:
            store_embeddings(
                chunks, 
                metadata={"filename": file.filename, "strategy": chunk_strategy}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to store embeddings: {str(e)}"
            )

        return {
            "filename": file.filename, 
            "chunks": len(chunks), 
            "message": "File processed successfully."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if db:
            db.close()


@app.post("/chat")
async def chat(user_input: str = Form(...)):
    """
    User sends input text and gets answer from ChatGroq LLM based on relevant document chunks.
    """
    try:
        # Validate input
        if not user_input or not user_input.strip():
            raise HTTPException(status_code=400, detail="User input cannot be empty")
        
        # Query chatbot
        try:
            answer = query_chatbot(user_input)
            
            if not answer:
                return {
                    "user_input": user_input, 
                    "answer": "No answer generated. Please try again."
                }
            
            return {"user_input": user_input, "answer": answer}
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Chatbot query failed: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )