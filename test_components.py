
import os
import sys
import google.generativeai as genai
from neurorun.body.droidrun_bridge import DroidRunBridge

def test_bridge():
    print("\n[TEST] Testing Bridge...")
    b = DroidRunBridge()
    if not b.adb_tool:
        print("[TEST] AdbTool failed init.")
    else:
        print(f"[TEST] AdbTool: {b.adb_tool}")
        # Introspect
        print(f"[TEST] Has open_app? {hasattr(b.adb_tool, 'open_app')}")
        print(f"[TEST] Dir: {dir(b.adb_tool)}")
        
def test_gemini():
    print("\n[TEST] Testing Gemini Import...")
    try:
        import google.generativeai
        print("[TEST] google.generativeai imported.")
    except ImportError:
        print("[TEST] google.generativeai MISSING.")

if __name__ == "__main__":
    test_gemini()
    test_bridge()
