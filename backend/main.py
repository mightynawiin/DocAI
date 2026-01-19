from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# ✅ FIXED: Import at TOP (not inside function)
from backend.document_loader import load_document
from backend.qa_engine import QAEngine  # ← CRITICAL!

app = FastAPI(title="Document Q&A App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

qa_engine = None  # Lazy load

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global qa_engine  # Reference global
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = load_document(file_path)
        qa_engine = QAEngine()  # Now QAEngine is defined!
        qa_engine.build_index(text)
        
        return {"message": "Document uploaded and indexed successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/summary")
async def get_summary():
    global qa_engine
    if qa_engine is None or qa_engine.document_text == "":
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    sentences = qa_engine.document_text.split('.')[:3]
    summary = '. '.join(sentences) + '.'
    return {"summary": summary[:500] + "..."}

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    global qa_engine
    if qa_engine is None:
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    try:
        answer = qa_engine.ask(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "DocAI Backend Running! Ready for uploads."}

@app.get("/docs")
async def docs():
    return {"docs": "Available at /docs (Swagger UI)"}
