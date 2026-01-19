from groq import Groq
import os

def generate_summary(text: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not found. Check .env file."

    client = Groq(api_key=api_key)

    if not text.strip():
        return "No text found in document."

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Summarize the document clearly and concisely."
            },
            {
                "role": "user",
                "content": text[:12000]
            }
        ]
    )

    return response.choices[0].message.content
