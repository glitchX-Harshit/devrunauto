
import os
try:
    from droidrun.tools import AdbTools
    DROIDRUN_API_AVAILABLE = True
except ImportError:
    DROIDRUN_API_AVAILABLE = False

class DroidRunBridge:
    def __init__(self):
        self.adb_tool = None
        if DROIDRUN_API_AVAILABLE:
            try:
                self.adb_tool = AdbTools()
                print("[Bridge] DroidRun AdbTools initialized.")
            except Exception as e:
                print(f"[Bridge] Failed to init AdbTools: {e}")
        else:
            print("[Bridge] DroidRun library not found.")

    def execute_action(self, action_type: str, selector: str) -> bool:
        """
        Executes an action via DroidRun Library.
        """
        print(f"[Bridge] Requesting: {action_type} -> {selector}")
        
        if not self.adb_tool:
            return False

        try:
            if action_type == "open_app":
                # Check for direct method
                if hasattr(self.adb_tool, "open_app"):
                    self.adb_tool.open_app(selector)
                    print(f"[Bridge] Executed open_app via AdbTools.")
                    return True
                
                # Check for shell method
                elif hasattr(self.adb_tool, "shell"):
                    print(f"[Bridge] Using AdbTools.shell to launch {selector}")
                    # Basic monkey launch
                    cmd = f"monkey -p {selector} -c android.intent.category.LAUNCHER 1"
                    if selector == "Settings":
                         cmd = "monkey -p com.android.settings -c android.intent.category.LAUNCHER 1"
                         
                    result = self.adb_tool.shell(cmd)
                    print(f"[Bridge] Shell result: {result}")
                    return True
                
                else:
                    print("[Bridge] AdbTools missing open_app and shell.")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[Bridge] DroidRun execution error: {e}")
            return False
