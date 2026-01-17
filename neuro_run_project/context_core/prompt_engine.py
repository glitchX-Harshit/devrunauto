import json

class PromptEngine:
    def __init__(self, context_manager):
        self.context_manager = context_manager

    def build_system_prompt(self, user_goal):
        """
        Constructs a system prompt by retrieving relevant context and profile data.
        """
        # Get static profile data
        profile = self.context_manager.profile
        
        # Get relevant vector memories
        memories = self.context_manager.query_memory(user_goal, n_results=2)
        memory_context = ""
        if memories and 'documents' in memories and memories['documents']:
             for doc_list in memories['documents']:
                 for doc in doc_list:
                     memory_context += f"- {doc}\n"

        system_prompt = f"""
You are NeuroRun, an intelligent orchestration agent for DroidRun.
Your goal is to generate a JSON execution plan for the user's request.

USER PROFILE:
Hardware: {json.dumps(profile.get('hardware_specs', {}))}
Preferences: {json.dumps(profile.get('preferences', {}))}
Habits: {json.dumps(profile.get('behavior_patterns', []))}

RELEVANT MEMORIES:
{memory_context}

INSTRUCTIONS:
1. Analyze the USER GOAL: "{user_goal}"
2. Use the profile and memories to optimize the plan (e.g., if network is slow, add delays).
3. Return ONLY a JSON list of steps.
"""
        return system_prompt
