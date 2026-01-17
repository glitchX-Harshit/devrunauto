import os
import json
import google.generativeai as genai
from context_core.prompt_engine import PromptEngine

class NeuroPlanner:
    def __init__(self, prompt_engine: PromptEngine):
        self.prompt_engine = prompt_engine
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("API Key not found. Please set GEMINI_API_KEY or DEEPSEEK_API_KEY in .env")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_plan(self, user_goal):
        """
        Generates a sequence of steps for DroidRun based on the user goal and context.
        """
        system_prompt = self.prompt_engine.build_system_prompt(user_goal)
        
        try:
            response = self.model.generate_content(system_prompt)
            text = response.text.strip()
            
            # Clean Markdown formatting
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            plan = json.loads(text)
            return plan
            
        except Exception as e:
            print(f"Error generating plan: {e}")
            return {"error": str(e)}
