
import sys
print(f"Python Version: {sys.version}")

try:
    import droidrun
    print("Imported droidrun")
except ImportError as e:
    print(f"Failed droidrun: {e}")

try:
    from llama_index.llms.google_genai import GoogleGenAI
    print("Imported GoogleGenAI")
except ImportError as e:
    print(f"Failed GoogleGenAI: {e}")

try:
    from llama_index.llms.gemini import Gemini
    print("Imported Gemini")
except ImportError as e:
    print(f"Failed Gemini: {e}")
