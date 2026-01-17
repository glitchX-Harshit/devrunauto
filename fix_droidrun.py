
import os
import sys
import shutil
import site

def fix():
    print("🔍 Searching for site-packages in .venv...")
    # Heuristic to find the site-packages of the current running python
    # which should be the venv python
    paths = sys.path
    target_path = None
    for p in paths:
        if "site-packages" in p and ".venv" in p:
            target_path = p
            break
            
    if not target_path:
        # Fallback: check standard location relative to executable
        # .venv/Lib/site-packages on Windows
        base = os.path.dirname(os.path.dirname(sys.executable))
        potential = os.path.join(base, "Lib", "site-packages")
        if os.path.exists(potential):
            target_path = potential
            
    if not target_path:
        print("❌ Could not locate site-packages in .venv")
        print(f"Debug sys.path: {sys.path}")
        sys.exit(1)
        
    print(f"📍 Site-packages: {target_path}")
    
    llama_index_path = os.path.join(target_path, "llama_index", "llms")
    gemini_path = os.path.join(llama_index_path, "gemini")
    google_path = os.path.join(llama_index_path, "google")
    
    if not os.path.exists(gemini_path):
        print(f"❌ llama_index.llms.gemini not found at {gemini_path}")
        # List what is in llama_index/llms
        if os.path.exists(llama_index_path):
            print(f"Contents of {llama_index_path}: {os.listdir(llama_index_path)}")
        sys.exit(1)
        
    if os.path.exists(google_path):
        print("⚠️ 'google' package already exists. Removing to re-patch...")
        shutil.rmtree(google_path)
        
    print("🛠️ Creating 'google' package...")
    shutil.copytree(gemini_path, google_path)
    
    init_file = os.path.join(google_path, "__init__.py")
    with open(init_file, "w") as f:
        f.write('from llama_index.llms.gemini import Gemini\n')
        f.write('Google = Gemini\n')
        f.write('__all__ = ["Google", "Gemini"]\n')
        
    print("✅ Patch Applied Successfully")

if __name__ == "__main__":
    fix()
