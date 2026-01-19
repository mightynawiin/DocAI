import os
from dotenv import load_dotenv
from groq import Groq

# ✅ LOAD .env FIRST (Railway + local both work)
load_dotenv()

class QAEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env or environment")
        
        self.client = Groq(api_key=api_key)
        self.document_text = ""
    
    def build_index(self, text: str):
        self.document_text = text[:12000]
        print(f"✅ Document indexed: {len(text)} chars")
    
    def ask(self, question: str) -> str:
        if not self.document_text:
            return "❌ No document uploaded. Please upload first."
        
        prompt = f"""<document>
{self.document_text}
</document>

QUESTION: {question}

ANSWER:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

