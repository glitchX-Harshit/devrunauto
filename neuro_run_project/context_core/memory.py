import json
import os
import chromadb
from chromadb.config import Settings

class ContextManager:
    def __init__(self, storage_dir="neuro_run_project/data"):
        self.storage_dir = storage_dir
        self.profile_path = os.path.join(self.storage_dir, "user_profile.json")
        self.chroma_path = os.path.join(self.storage_dir, "chroma_db")
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize JSON Profile
        if not os.path.exists(self.profile_path):
            self.profile = {
                "hardware_specs": {},
                "preferences": {},
                "credentials_map": {}, 
                "behavior_patterns": []
            }
            self.save_profile()
        else:
            self.load_profile()
            
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(name="user_context")

    def load_profile(self):
        try:
            with open(self.profile_path, 'r') as f:
                self.profile = json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
            self.profile = {}

    def save_profile(self):
        try:
            with open(self.profile_path, 'w') as f:
                json.dump(self.profile, f, indent=4)
        except Exception as e:
            print(f"Error saving profile: {e}")

    def update_profile(self, key, value, category="preferences"):
        """
        Updates a specific category in the user profile.
        category: 'preferences', 'hardware_specs', 'credentials_map', 'behavior_patterns'
        """
        if category not in self.profile:
            self.profile[category] = {}
        
        # behavior_patterns is a list
        if category == "behavior_patterns":
            if value not in self.profile[category]:
                self.profile[category].append(value)
        else:
            self.profile[category][key] = value
            
        self.save_profile()

    def add_memory(self, text, metadata=None):
        """Adds a text memory to ChromaDB."""
        if metadata is None:
            metadata = {}
        
        # Simple ID generation
        import uuid
        mem_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[mem_id]
        )

    def query_memory(self, query_text, n_results=3):
        """Retrieves relevant memories."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
