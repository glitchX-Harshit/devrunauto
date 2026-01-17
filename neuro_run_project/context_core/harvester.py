import os
import json
import asyncio
import google.generativeai as genai
from .memory import ContextManager

class InsightHarvester:
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        # Configure API
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if api_key:
             genai.configure(api_key=api_key)
             self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
             print("Warning: No API Key found for InsightHarvester")
             self.model = None

    async def extract_insights(self, chat_message):
        """
        Analyzes the latest message for permanent preferences or facts.
        Runs asynchronously to not block the main thread.
        """
        if not self.model:
            return

        prompt = f"""
You are a background fact-checker. 
Analyze the user's latest message: "{chat_message}"
Extract any PERMANENT preferences, hardware details, or recurring habits. 
Return strictly JSON updates in the following format. If nothing new is found, return null.

Target Format:
{{
    "hardware_specs": {{ "key": "value" }},
    "preferences": {{ "key": "value" }},
    "behavior_patterns": ["new pattern string"]
}}
"""
        
        try:
            # mimic async call if library doesn't support native async execution easily
            # But genai library generally supports async methods if using `generate_content_async`
            response = await self.model.generate_content_async(prompt)
            
            text = response.text.strip()
            if text.lower() == "null":
                return

            # Clean code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text)
            
            if data:
                print(f"[InsightHarvester] Found new insights: {data}")
                # Update Context
                if "hardware_specs" in data and data["hardware_specs"]:
                    for k, v in data["hardware_specs"].items():
                        self.context_manager.update_profile(k, v, "hardware_specs")
                
                if "preferences" in data and data["preferences"]:
                    for k, v in data["preferences"].items():
                        self.context_manager.update_profile(k, v, "preferences")
                        
                if "behavior_patterns" in data and data["behavior_patterns"]:
                    for pattern in data["behavior_patterns"]:
                        self.context_manager.update_profile(None, pattern, "behavior_patterns")

        except Exception as e:
            print(f"[InsightHarvester] Error: {e}")
