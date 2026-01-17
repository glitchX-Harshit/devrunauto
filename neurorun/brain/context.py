
import json
import os

class ContextManager:
    def __init__(self, profile_path: str = "user_profile.json"):
        self.profile_path = profile_path
        self.profile = self.load_profile()

    def load_profile(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r") as f:
                return json.load(f)
        return {"keyboard_lag_ms": 200}
