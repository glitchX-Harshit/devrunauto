
import os
import time
import json
import google.generativeai as genai
from .adb_manager import ADBManager

class SmartAgent:
    def __init__(self, api_key: str):
        self.adb = ADBManager()
        self.adb.connect()
        try:
           genai.configure(api_key=api_key)
           self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Using faster model if available
        except:
           self.model = genai.GenerativeModel('gemini-1.5-flash')

    def capture_state(self):
        """Captures XML and simplifies it for the LLM."""
        xml = self.adb.get_xml_dump()
        if not xml: return "Screen is empty or protected."
        
        # Simplify: Extract only nodes with text or content-desc
        import xml.etree.ElementTree as ET
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
            elements = []
            for node in tree.getroot().iter('node'):
                txt = node.attrib.get('text', '')
                desc = node.attrib.get('content-desc', '')
                bounds = node.attrib.get('bounds', '')
                if txt or desc:
                    label = txt if txt else desc
                    # Basic bounds check to ignore tiny/invisible (optional)
                    elements.append(f"Element: '{label}' Bounds: {bounds}")
            return "\n".join(elements[-50:]) # Send last 50 elements to avoid context limit issues in tight loop
        except:
             return "XML Parse Error"
             
    def act(self, goal: str, max_steps: int = 10):
        print(f"\n--- SmartAgent Goal: {goal} ---")
        history = []
        
        for i in range(max_steps):
            print(f"\nStep {i+1}: Observing...")
            screen_content = self.capture_state()
            
            prompt = f"""
            You are a mobile agent.
            Goal: {goal}
            
            Screen Content (Simplified XML):
            {screen_content}
            
            Action History:
            {history}
            
            Available Actions:
            - TAP_TEXT("text"): Tap element containing text
            - TYPE("text"): Type text
            - ENTER: Press Enter/Search
            - HOME: Go Home
            - WAIT: Wait 2 seconds
            - FINISH("answer"): Return final answer
            
            Output strictly one of the above formats. No markdown.
            """
            
            try:
                response = self.model.generate_content(prompt)
                action_str = response.text.strip().replace("`", "")
                print(f"Agent Decided: {action_str}")
                
                history.append(action_str)
                
                if "FINISH" in action_str:
                    return action_str.replace("FINISH", "").strip("()\"'")
                
                elif "TAP_TEXT" in action_str:
                    target = action_str.split('"')[1]
                    self.adb.tap_text(target)
                    time.sleep(2)
                    
                elif "TYPE" in action_str:
                    text = action_str.split('"')[1]
                    self.adb.input_text(text)
                    
                elif "ENTER" in action_str:
                     self.adb._run_cmd(["shell", "input", "keyevent", "66"])
                     time.sleep(2)

                elif "HOME" in action_str:
                    self.adb.press_home()
                    time.sleep(1)

                elif "WAIT" in action_str:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error in loop: {e}")
                time.sleep(1)
        
        return "Max steps reached without definitive answer."
