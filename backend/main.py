from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from backend.document_loader import load_document

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

qa_engine = None  # ✅ LAZY LOAD - FIXED!

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global qa_engine
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = load_document(file_path)
        qa_engine = QAEngine()  # ✅ CREATE HERE (after env vars load)
        qa_engine.build_index(text)
        
        return {"message": "Document uploaded and indexed successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/summary")
async def get_summary():
    global qa_engine
    if not qa_engine or not qa_engine.document_text:
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    sentences = qa_engine.document_text.split('.')[:3]
    summary = '. '.join(sentences) + '.'
    return {"summary": summary or "Document ready!"}

@app.post("/ask")
async def ask_question(question: str):
    global qa_engine
    if not qa_engine:
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    try:
        answer = qa_engine.ask(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "DocAI Backend Running! Upload at /docs"}
