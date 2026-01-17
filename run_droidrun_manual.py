
import asyncio
import logging
import os
import io
from dotenv import load_dotenv

# Force UTF-8 for console output to avoid encoding errors
import sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
# Ensure GOOGLE_API_KEY is set
key = os.environ.get("GEMINI_API_KEY")
if key:
    os.environ["GOOGLE_API_KEY"] = key

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("droidrun")

try:
    from droidrun.agent.droid import DroidAgent
    from droidrun.agent.utils.llm_picker import load_llm
    from droidrun.tools import AdbTools
    from droidrun.adb import DeviceManager
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("--- DroidRun Manual 0.3.0 Fixed ---")
    
    # 1. Device
    try:
        dm = DeviceManager()
        devices = await dm.list_devices()
        if not devices:
            print("No device found!")
            return
        serial = devices[0].serial
        print(f"Device: {serial}")
    except Exception as e:
        print(f"Device Discovery Error: {e}")
        return
    
    # 2. Tools
    tools = AdbTools(serial=serial)
    
    # 3. LLM
    try:
        print("Loading LLM...")
        llm = load_llm(
            provider_name="GoogleGenAI", 
            model="models/gemini-2.0-flash",
            api_key=os.environ["GOOGLE_API_KEY"]
        )
        print("LLM Loaded")
    except Exception as e:
        print(f"LLM Load Error: {e}")
        # Fallback to other model names if needed
        return

    # 4. Agent
    command = "open swiggy and check price of chicken nugget. output the price"
    
    try:
        print("Initializing Agent...")
        agent = DroidAgent(
            goal=command,
            llm=llm,
            tools=tools,
            max_steps=15,
            debug=True,
            vision=True # Enable vision as requested by user "see things"
        )
        
        print("Running Agent...")
        handler = agent.run()
        
        # Stream events if possible (handler is WorkflowHandler)
        if hasattr(handler, "stream_events"):
            async for event in handler.stream_events():
                print(f"Event: {type(event).__name__}")
                
        result = await handler
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
