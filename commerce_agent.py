import os
import json
import argparse
import asyncio
import re
import sys
import io
from dotenv import load_dotenv

# Ensure we can import neurorun
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from neurorun.orchestrator import NeuroOrchestrator
except ImportError:
    print("Error: Could not import NeuroOrchestrator. Ensure neurorun/orchestrator.py exists.")
    sys.exit(1)

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
# Ensure keys
key = os.environ.get("GEMINI_API_KEY")
if key:
    os.environ["GOOGLE_API_KEY"] = key

def parse_price(price_str):
    if not price_str: return float('inf')
    try:
        clean = str(price_str).lower().replace(',', '').replace('₹', '').replace('rs', '').replace('rs.', '').strip()
        match = re.search(r'\d+(\.\d+)?', clean)
        return float(match.group()) if match else float('inf')
    except:
        return float('inf')

async def perform_search(app_name, query, item_type="product"):
    """
    Executes search using NeuroOrchestrator (The 'Super-Agent')
    """
    print(f"\n[Status] 🧠 NeuroOrchestrator activating for {app_name}...")
    
    # Initialize Orchestrator
    orchestrator = NeuroOrchestrator(api_key=os.environ["GOOGLE_API_KEY"])
    
    # High-level Goal for the Brain
    goal = (
        f"Open {app_name} and search for '{query}'. "
        f"Find the top result for {item_type}. "
        f"Read its price and rating from the screen. "
        f"Return the data strictly as JSON: {{'title': '...', 'price': '...', 'rating': '...'}}"
        f"If the app is not installed or fails to load, return status failed."
    )
    
    result = await orchestrator.run_mission(goal)
    
    if isinstance(result, dict) and result.get('status') == 'success':
        data = result.get('data', {})
        # Normalize keys
        return {
            "platform": app_name,
            "status": "success",
            "items": [data], # Orchestrator returns best item usually
            "best_item": {
                "title": data.get('title', 'Unknown'),
                "price": data.get('price', '0'),
                "rating": data.get('rating', '0'),
                "numeric_price": parse_price(data.get('price', '0'))
            }
        }
    else:
        return {
            "platform": app_name,
            "status": "failed",
            "error": result.get('error', 'Unknown Error') if isinstance(result, dict) else str(result)
        }

async def main_async():
    parser = argparse.ArgumentParser(description="DroidRun Commerce Agent (NeuroOrchestrator)")
    parser.add_argument("--task", choices=['shopping', 'food'], default='shopping', help="Type of task")
    parser.add_argument("--query", required=True, help="Item to search for")
    
    args = parser.parse_args()
    
    platforms = []
    item_type = "product" # default
    if args.task == "shopping":
        platforms = ["Amazon", "Flipkart"]
        item_type = "product"
    elif args.task == "food":
        platforms = ["Zomato", "Swiggy"]
        item_type = "food item"
        
    results = {}
    
    for plat in platforms:
        res = await perform_search(plat, args.query, item_type)
        results[plat.lower()] = res
        
    # Comparison Logic
    print(json.dumps(results, indent=2))

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()