
import os
import sys

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from body.adb_manager import ADBManager
from body.droidrun_bridge import DroidRunBridge
from brain.planner import Planner
from brain.context import ContextManager

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"')

def main():
    print("Initializing NeuroRun...")
    load_env()
    
    api_key = os.environ.get("GEMINI_API_KEY")

    # 1. Initialize ADBManager
    adb = ADBManager()
    if not adb.connect():
        print("Failed to connect to device. Aborting.")
        return

    # 2. Testing Planner (Brain)
    print("\n--- Testing Brain ---")
    planner = Planner(api_key=api_key)
    ctx = ContextManager().profile
    plan = planner.plan_steps("Open Settings and turn on WiFi", ctx)
    print(f"Plan: {plan}")

    # 3. Execution Task: Launch Settings (Body)
    print("\n--- Testing Body ---")
    # Initialize Bridge (no path needed now)
    bridge = DroidRunBridge()

    print("Executing 'Launch Settings' via Bridge...")
    success = bridge.execute_action("open_app", "Settings")
    
    if success:
        print("Bridge execution successful.")
    else:
        print("Bridge execution failed. Attempting fallback...")
        adb.launch_app("com.android.settings")
    
    print("\nSystem Online")

if __name__ == "__main__":
    main()
