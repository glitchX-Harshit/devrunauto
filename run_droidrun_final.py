
import subprocess
import os
import sys

def main():
    print("--- DroidRun Final Execution ---")
    
    # Env
    env = os.environ.copy()
    env["GOOGLE_API_KEY"] = os.environ.get("GEMINI_API_KEY")
    
    cmd = [
        sys.executable, "-m", "droidrun", "run", 
        "open swiggy and check price of chicken nugget. output the price",
        "--provider", "GoogleGenAI",
        "--model", "models/gemini-2.0-flash", # The Magic String
        "--debug" # Enable debug to see Portal errors
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, env=env, check=False) # Check False to not crash script on exit 1
    except KeyboardInterrupt:
        print("Stopped by User")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
