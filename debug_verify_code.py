
import os
import droidrun.agent.codeact.codeact_agent as c
print(f"File: {c.__file__}")

with open(c.__file__, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 105 <= i <= 115:
            print(f"{i+1}: {line.rstrip()}")
