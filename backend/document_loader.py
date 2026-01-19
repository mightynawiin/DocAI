import PyPDF2
import docx
import os

def load_document(file_path):
    """Extract text from PDF, DOCX, or TXT"""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return extract_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return extract_docx(file_path)
        elif ext == '.txt':
            return open(file_path, 'r', encoding='utf-8').read()
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        print(f"Error loading document: {e}")
        return "Error reading document"

def extract_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
