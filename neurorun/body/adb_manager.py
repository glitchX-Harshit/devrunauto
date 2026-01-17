
import subprocess
import time
import os
import re
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, List

class ADBManager:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.connected = False
        self._check_connection()

    def _check_connection(self):
        self.connect()

    def _run_cmd(self, args: list[str], timeout: int = 20) -> tuple[bool, str]:
        """Runs an ADB command and returns success/output."""
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout.strip())
        except subprocess.TimeoutExpired:
             return (False, "Timeout")
        except FileNotFoundError:
            return (False, "ADB not found in PATH")
        except Exception as e:
            return (False, str(e))

    def connect(self) -> bool:
        success, output = self._run_cmd(["devices"])
        if not success: return False
        
        lines = output.splitlines()
        for line in lines[1:]:
            if "device" in line and "offline" not in line:
                parts = line.split()
                if parts:
                    self.device_id = parts[0]
                    self.connected = True
                    return True
        return False

    def get_xml_dump(self) -> Optional[str]:
        """Dumps the current UI hierarchy to XML."""
        # Clean up old
        self._run_cmd(["shell", "rm", "/sdcard/window_dump.xml"])
        
        # Dump
        self._run_cmd(["shell", "uiautomator", "dump"])
        
        # Cat
        success, output = self._run_cmd(["shell", "cat", "/sdcard/window_dump.xml"])
        if success and "UI hierchary dumped" not in output: # "UI hierchary dumped" is printout, not content
             return output
        return None

    def find_element_by_text(self, text: str, regex: bool = False) -> Optional[Tuple[int, int]]:
        """Finds center coordinates of an element containing text."""
        xml_str = self.get_xml_dump()
        if not xml_str: return None
        
        try:
            # Simple parse helper
            # We treat the XML as string for loose matching if regex, or strict xml parse
            tree = ET.ElementTree(ET.fromstring(xml_str))
            root = tree.getroot()
            
            for node in root.iter('node'):
                node_text = node.attrib.get('text', '')
                content_desc = node.attrib.get('content-desc', '')
                
                match = False
                if regex:
                    if (node_text and re.search(text, node_text, re.IGNORECASE)) or \
                       (content_desc and re.search(text, content_desc, re.IGNORECASE)):
                        match = True
                else:
                    if (text.lower() in node_text.lower()) or (text.lower() in content_desc.lower()):
                        match = True
                
                if match:
                    bounds = node.attrib.get('bounds')
                    if bounds:
                        # [x1,y1][x2,y2]
                        m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                        if m:
                            x1, y1, x2, y2 = map(int, m.groups())
                            return ((x1 + x2) // 2, (y1 + y2) // 2)
            return None
        except Exception as e:
            print(f"XML Parse Error: {e}")
            return None

    def tap(self, x: int, y: int):
        self._run_cmd(["shell", "input", "tap", str(x), str(y)])

    def tap_text(self, text: str) -> bool:
        coords = self.find_element_by_text(text)
        if coords:
            print(f"Tapping '{text}' at {coords}")
            self.tap(*coords)
            return True
        print(f"Could not find text: '{text}'")
        return False

    def input_text(self, text: str):
        # Escape spaces
        escaped = text.replace(" ", "%s")
        self._run_cmd(["shell", "input", "text", escaped])
        
    def press_home(self):
        self._run_cmd(["shell", "input", "keyevent", "KEYCODE_HOME"])

    def launch_app(self, package_name: str):
        self._run_cmd(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
