
import os
import sys

# Add venv site-packages manually just in case
# But we will run with venv python so it should be fine.

def debug_gemini():
    print("--- Debugging Gemini Integration ---")
    try:
        from llama_index.llms.gemini import Gemini
        print("✅ Successfully imported Gemini from llama_index.llms.gemini")
    except ImportError as e:
        print(f"❌ Failed to import Gemini: {e}")
        return

    try:
        # Try our patched path
        from llama_index.llms.google import Google
        print("✅ Successfully imported Google from llama_index.llms.google")
    except ImportError as e:
        print(f"❌ Failed to import Google (Patch broken?): {e}")

    # Check API Key
    key = os.environ.get("GOOGLE_API_KEY")
    print(f"API Key present: {bool(key)}")
    
    if key:
        try:
            llm = Gemini(model="models/gemini-1.5-flash", api_key=key)
            print("✅ Initialized Gemini LLM")
            resp = llm.complete("Hello")
            print(f"✅ Gemini Response: {resp}")
        except Exception as e:
            print(f"❌ Gemini Execution Failed: {e}")

if __name__ == "__main__":
    # Load .env manually
    from dotenv import load_dotenv
    load_dotenv()
    debug_gemini()
