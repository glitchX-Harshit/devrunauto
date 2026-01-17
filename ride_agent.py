import os
import sys
import io
import asyncio
import re
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
if os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

def clean_price(price_raw):
    if not price_raw: return None
    try:
        clean = str(price_raw).lower().replace(',', '').replace('₹', '').replace('rs', '').replace('rs.', '').strip()
        match = re.search(r'\d+(\.\d+)?', clean)
        return float(match.group()) if match else None
    except:
        return None

async def run_ride_check(app_name, pickup, loop_drop):
    """
    Runs NeuroOrchestrator for Ride App.
    """
    print(f"\n[RideAgent] 🧠 NeuroOrchestrator activating for {app_name}...")
    
    orchestrator = NeuroOrchestrator(api_key=os.environ["GOOGLE_API_KEY"])
    
    goal = (
        f"Go to Home Screen. "
        f"Open {app_name}. "
        f"Book a ride from '{pickup}' to '{loop_drop}'. "
        f"Wait for the price options to appear. "
        f"Read the cheapest price (e.g. UberGo, Mini) and the ETA. "
        f"Return the data strictly as JSON: {{'app': '{app_name}', 'type': 'UberGo/Mini', 'price': '...', 'eta': '...'}}"
        f"If the price is not visible or app fails, return status failed."
    )
    
    result = await orchestrator.run_mission(goal)
    
    if isinstance(result, dict) and result.get('status') == 'success':
        data = result.get('data', {})
        data['numeric_price'] = clean_price(data.get('price'))
        return data
    else:
        return {"status": "failed", "error": result.get('error', 'Unknown') if isinstance(result, dict) else str(result)}

async def main():
    # Example Usage
    pickup = "Current Location"
    drop = "Viviana Mall"
    
    # Run Uber
    uber_res = await run_ride_check("Uber", pickup, drop)
    print(f"\n[Result] Uber: {uber_res}")
    
    # Run Ola (can uncomment when ready)
    # ola_res = await run_ride_check("Ola", pickup, drop)
    
    if uber_res.get('numeric_price'):
        print(f"Uber Price: {uber_res['numeric_price']}")
    else:
        print("Uber Failed.")

if __name__ == "__main__":
    asyncio.run(main())
