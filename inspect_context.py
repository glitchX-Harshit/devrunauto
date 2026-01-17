
from llama_index.core.workflow import Context
import inspect

print("--- Context Inspection ---")
print(f"Context dir: {dir(Context)}")
print(f"Has get: {hasattr(Context, 'get')}")

try:
    c = Context()
    print(f"Instance dir: {dir(c)}")
except Exception as e:
    print(e)
