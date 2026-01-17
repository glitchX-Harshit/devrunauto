
import os
import sys

# Path Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neurorun.body.smart_agent import SmartAgent

def load_env():
    # ... (Same env loader as before) ...
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v.strip('"')

def main():
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    agent = SmartAgent(api_key)
    
    print("Beginning Market Research...")
    
    # 1. Check Swiggy
    # Launch done manually via simple adb first to ensure start state
    agent.adb.press_home()
    agent.adb.launch_app("in.swiggy.android")
    # Loop
    swiggy_price = agent.act('Search for "McDonalds", click it, find "Chicken McNuggets" or "Chicken Nuggets", and tell me the price. Format: "Price: Rs. X"', max_steps=15)
    print(f"Swiggy Result: {swiggy_price}")
    
    # 2. Check Zomato
    agent.adb.press_home()
    agent.adb.launch_app("com.application.zomato")
    zomato_price = agent.act('Search for "McDonalds", click it, find "Chicken McNuggets" or "Chicken Nuggets", and tell me the price. Format: "Price: Rs. X"', max_steps=15)
    print(f"Zomato Result: {zomato_price}")
    
    # Simple report
    print("\n--- FINAL REPORT ---")
    print(f"Swiggy: {swiggy_price}")
    print(f"Zomato: {zomato_price}")

if __name__ == "__main__":
    main()
