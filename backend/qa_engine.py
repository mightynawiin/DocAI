import os
from groq import Groq

class QAEngine:
    def __init__(self):
        # ✅ Railway/Local BOTH work - NO dotenv needed
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing - set in Railway Variables or local .env")
        
        self.client = Groq(api_key=api_key)
        self.document_text = ""
    
    def build_index(self, text: str):
        self.document_text = text[:12000]
        print(f"✅ Document indexed: {len(text)} chars")
    
    def ask(self, question: str) -> str:
        if not self.document_text:
            return "❌ No document uploaded first."
        
        prompt = f"""<document>{self.document_text}</document>
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
            return f"Groq error: {str(e)}"
