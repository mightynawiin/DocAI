from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# ✅ FIXED IMPORTS
from backend.document_loader import load_document
from backend.qa_engine import QAEngine

app = FastAPI(title="Document Q&A App")

# ✅ CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

qa_engine = QAEngine()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = load_document(file_path)
        qa_engine.build_index(text)
        
        return {"message": "Document uploaded and indexed successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/summary")  # ✅ MISSING ENDPOINT ADDED
async def get_summary():
    if not qa_engine.document_text:
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    # Simple summary (3-sentence version of document)
    sentences = qa_engine.document_text.split('.')[:3]
    summary = '. '.join(sentences) + '.'
    return {"summary": summary or "Document processed successfully - ready for questions!"}

@app.post("/ask")
async def ask_question(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="Question required")
    
    try:
        answer = qa_engine.ask(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "DocAI Backend Running! Upload at /docs"}
