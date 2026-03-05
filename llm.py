from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()  # ← זה מה שחסר — טוען את ה-.env לפני יצירת ה-client

client = OpenAI(
    base_url="https://api.groq.com/openai/v1", 
    api_key=os.getenv("OPENAI_API_KEY") 
)

PROMPT_PATH = Path(__file__).parent / "system-prompt" / "prompt-7.md"

def load_system_prompt() -> str:
    """קוראת את קובץ ה-markdown מהדיסק בכל קריאה — שינוי ב-prompt נכנס מיד"""
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_command(user_input: str) -> str:
    """שולחת טקסט חופשי ל-GPT ומחזירה פקודת טרמינל נקייה"""
    if not user_input.strip():
        return ""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": user_input},
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()