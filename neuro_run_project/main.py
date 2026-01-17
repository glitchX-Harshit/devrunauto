import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from context_core.memory import ContextManager
from context_core.harvester import InsightHarvester
from context_core.prompt_engine import PromptEngine
from planner import NeuroPlanner
from droidrun_bridge import DroidRunBridge

# Load environment variables
load_dotenv()
# Also try loading from parent directory if not found (development convenience)
if not os.getenv("GEMINI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

async def main():
    print("Welcome to NeuroRun (Adaptive Agent Core)")
    
    # Initialize Components
    print("Initializing Context Manager...")
    context_manager = ContextManager()
    
    print("Initializing Harvester...")
    harvester = InsightHarvester(context_manager)
    
    print("Initializing Planner...")
    prompt_engine = PromptEngine(context_manager)
    try:
        planner = NeuroPlanner(prompt_engine)
    except ValueError as e:
        print(f"Error: {e}")
        return

    bridge = DroidRunBridge()
    
    print("System Ready. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\nUser> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if not user_input.strip():
                continue

            # 1. Background Learning (Fire and Forget-ish)
            # We await it here for simplicity in this loop, but in a real event loop 
            # we might create a task to let it run parallel. 
            # "The Harvester must run asynchronously... so it doesn't block the Planner"
            # Since the planner depends on context, it might be good to await critical updates,
            # but per requirements "doesn't block planner", we should spawn it.
            # However, if I spawn it, the Planner might use stale data for *this* turn.
            # But the requirement says "immediately update context", implying speed.
            # Let's create a task.
            asyncio.create_task(harvester.extract_insights(user_input))
            
            # 2. Planning
            print("Thinking...")
            plan = planner.generate_plan(user_input)
            
            if "error" in plan:
                print(f"Planning failed: {plan['error']}")
                continue

            # 3. Execution
            print("Executing Plan...")
            bridge.execute_sequence(plan)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
