import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class QAEngine:
    def __init__(self):
        self.document_text = ""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def build_index(self, text: str):
        self.document_text = text[:12000]
        print(f"✅ Document indexed: {len(text)} chars")
    
    def ask(self, question: str) -> str:
        if not self.document_text:
            return "❌ No document uploaded. Please upload first."
        
        # ✅ FIXED: Use ACTIVE Groq models (2026)
        prompt = f"""<document>
{self.document_text}
</document>

INSTRUCTIONS: Answer using ONLY the document above. 
If answer not found, say "Not in document".
Be concise.

QUESTION: {question}

ANSWER:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # ✅ ACTIVE & FASTEST
                # Alternative: "mixtral-8x7b-32768" or "gemma2-9b-it"
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content.strip()
            
            if "not in document" in answer.lower():
                return "ℹ️ No specific information found for this question."
            
            return answer
            
        except Exception as e:
            print(f"Groq Error: {e}")
            # ✅ FALLBACK: Smart keyword search
            return self._fallback_search(question)
    
    def _fallback_search(self, question: str) -> str:
        """Smart backup if Groq fails"""
        if not self.document_text:
            return "No document available."
        
        q_words = question.lower().split()
        sentences = self.document_text.split('.')
        best_match = ""
        max_score = 0
        
        for sent in sentences:
            score = sum(1 for word in q_words if word in sent.lower())
            if score > max_score:
                max_score = score
                best_match = sent.strip()
        
        if max_score > 0:
            return f"**Found:** {best_match[:300]}..."
        return "No matching information found in document."
