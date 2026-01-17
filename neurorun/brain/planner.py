
import os
import json
import google.generativeai as genai
from typing import List

class Planner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not api_key:
            print("Warning: No API Key provided to Planner")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.available = True
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                self.available = False

    def plan_steps(self, goal: str, context: dict) -> List[str]:
        """
        Converts a goal into a list of steps using Gemini.
        """
        if not hasattr(self, 'available') or not self.available:
            print("[Planner] Gemini not available. Returning mock plan.")
            return ["Mock Action 1", "Mock Action 2"]

        print(f"[Planner] Planning for: {goal}")
        
        prompt = f"""
        You are a mobile automation planner.
        Goal: {goal}
        Context: {json.dumps(context)}
        
        Return a JSON list of strings, where each string is a high-level action.
        Example: ["open_app Settings", "tap WiFi", "input_text password"]
        
        Output JSON only.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up potential markdown code blocks
            if text.startswith("```"):
                # find first newline
                first_nl = text.find("\n")
                if first_nl != -1:
                    text = text[first_nl+1:]
                if text.endswith("```"):
                    text = text[:-3]
            
            steps = json.loads(text)
            print(f"[Planner] Generated Plan: {steps}")
            return steps
        except Exception as e:
            print(f"[Planner] Planning failed: {e}")
            return ["Error in planning"]
