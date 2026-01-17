
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"Key present: {bool(api_key)}")

print("\n--- Listing Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"List Error: {e}")

print("\n--- Testing Generation (gemini-2.0-flash) ---")
try:
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    response = model.generate_content("Hello")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Error 2.0: {e}")

print("\n--- Testing Generation (gemini-1.5-flash) ---")
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Error 1.5: {e}")
