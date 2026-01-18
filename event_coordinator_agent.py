import os
import json
import argparse
import asyncio
import sys
from dotenv import load_dotenv

# --- DroidRun Professional Architecture Imports ---
try:
    from droidrun.agent.droid import DroidAgent
    from droidrun.agent.utils.llm_picker import load_llm
    from droidrun.config_manager import DroidrunConfig, AgentConfig, ManagerConfig, ExecutorConfig, TelemetryConfig
except ImportError:
    print("CRITICAL ERROR: 'droidrun' library not found or incompatible version.")
    print("Please ensure you have installed it: pip install droidrun")
    sys.exit(1)

# Load environment variables
load_dotenv()

class EventCoordinatorAgent:
    """
    Agent to coordinate events by sending invites via messaging apps (WhatsApp).
    """
    
    def __init__(self, provider="gemini", model="models/gemini-2.5-flash"):
        self.provider = provider
        self.model = model
        self._ensure_api_keys()

    def _ensure_api_keys(self):
        if self.provider == "gemini" and not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
             print("[Warn] GEMINI_API_KEY not found in env, checking GOOGLE_API_KEY")

    async def send_invite(self, contact_name: str, message: str, app_name: str = "WhatsApp") -> dict:
        """
        Sends a specific message to a contact using the specified app.
        """
        print(f"\n[EventCoordinator] 📨 Sending Invite to: {contact_name} on {app_name}")
        
        # Define Goal: Open App -> Find Contact -> Send Message
        goal = (
            f"Open the app '{app_name}'. "
            f"Click on the 'Search' icon or bar. "
            f"Type the contact name '{contact_name}'. "
            f"Wait for the contact '{contact_name}' to appear in the list. "
            f"Click on the contact to open the chat. "
            f"Type the following message exactly: '{message}'. "
            f"Click the 'Send' button (usually a paper airplane icon). "
            f"Return a strict JSON object with keys: 'status' (success/failed), 'contact', 'time_sent'. "
        )

        # --- Professional Config Setup ---
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        provider_name = "GoogleGenAI" if self.provider == "gemini" else self.provider

        llm = load_llm(
            provider_name=provider_name,
            model=self.model,
            api_key=api_key
        )

        # Enable Vision for robust UI interaction
        manager_config = ManagerConfig(vision=True)
        executor_config = ExecutorConfig(vision=True)
        
        agent_config = AgentConfig(
            reasoning=True,
            manager=manager_config,
            executor=executor_config
        )
        
        telemetry_config = TelemetryConfig(enabled=False)
        
        config = DroidrunConfig(
            agent=agent_config,
            telemetry=telemetry_config
        )

        agent = DroidAgent(
            goal=goal,
            llms=llm,
            config=config
        )

        result_data = {"contact": contact_name, "status": "failed"}

        try:
            print(f"[EventCoordinator] 🧠 Executing Agent Logic...")
            result = await agent.run()
            
            # --- Parsing ---
            if result:
                if hasattr(result, 'reason'):
                     clean_json = str(result.reason).strip()
                else:
                     clean_json = str(result).strip()

                if "<request_accomplished" in clean_json:
                    try:
                        clean_json = clean_json.split(">")[1].split("</request_accomplished>")[0].strip()
                    except IndexError:
                        pass
                
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                if clean_json.startswith("{"):
                    try:
                        data = json.loads(clean_json)
                        result_data.update(data)
                        result_data["status"] = "success"
                    except json.JSONDecodeError:
                        print(f"[Warn] JSON Decode Error: {clean_json}")
            
            return result_data

        except Exception as e:
            print(f"[Error] Failed to send to {contact_name}: {e}")
            return result_data

async def main():
    parser = argparse.ArgumentParser(description="Event Coordinator Agent")
    parser.add_argument("--contacts", required=True, help="Comma-separated list of contact names/numbers")
    parser.add_argument("--event", required=True, help="Name of the event")
    parser.add_argument("--date", required=True, help="Date of event")
    parser.add_argument("--time", required=True, help="Time of event")
    parser.add_argument("--location", required=True, help="Location of event")
    parser.add_argument("--app", default="WhatsApp", help="Messaging App to use")
    
    args = parser.parse_args()
    
    # 1. Construct Message
    invite_message = (
        f"Hi! You are invited to the *{args.event}* "
        f"on *{args.date}* at *{args.time}*. "
        f"Location: {args.location}. "
        f"See you there!"
    )
    
    print(f"\n--- Event Coordinator ---")
    print(f"Event: {args.event}")
    print(f"Message Preview: \"{invite_message}\"")
    print(f"Contacts: {args.contacts}")
    print("-------------------------\n")

    agent = EventCoordinatorAgent(model="models/gemini-2.5-flash")
    
    contact_list = [c.strip() for c in args.contacts.split(",")]
    results = {}

    for contact in contact_list:
        res = await agent.send_invite(contact, invite_message, args.app)
        results[contact] = res
        print(f"✅ Result for {contact}: {res.get('status')}")
        # Cooldown
        await asyncio.sleep(2)

    print("\n--- Final Status ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
