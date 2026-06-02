"""Quick test — list available Gemini models then call one."""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded: {api_key[:10]}...")

from google import genai

client = genai.Client(api_key=api_key)

print("\nAvailable models:")
for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(" -", model.name)

# Try the most common current model names
for model_name in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest"]:
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say hello in one word.",
        )
        print(f"\nWorking model: {model_name}")
        print("Response:", response.text)
        break
    except Exception as e:
        print(f"  {model_name} failed: {e}")
