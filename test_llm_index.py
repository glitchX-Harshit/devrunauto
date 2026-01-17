
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

print(f"API Key present: {bool(api_key)}")

try:
    from llama_index.llms.gemini import Gemini
    print("Imported Gemini")
except ImportError:
    print("Failed to import Gemini")
    exit(1)

# Test cases for model names
model_names = [
    "models/gemini-1.5-flash",
    "gemini-1.5-flash",
    "models/gemini-pro",
    "gemini-pro"
]

for m in model_names:
    print(f"\nTesting model: {m}")
    try:
        llm = Gemini(model=m, api_key=api_key)
        resp = llm.complete("Hello")
        print(f"SUCCESS: {resp}")
        break 
    except Exception as e:
        print(f"FAILED: {e}")
