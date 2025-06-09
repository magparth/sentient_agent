import sys
import os

# 🚀 FORCE local Sentient-Agent-Framework-main
sys.path.insert(0, r"C:\Users\parth\Downloads\Sentient-Agent-Framework-main\Sentient-Agent-Framework-main\src")

# Debug sys.path
print("👉 sys.path is now:")
for p in sys.path:
    print(p)

# Now import
from sentient_agent_framework.implementation.default_server import DefaultServer
from wrapped_agent import WrappedZeruScoreAgent

import sentient_agent_framework.implementation.default_server as ds
print(f"👉 DefaultServer LOADED FROM: {ds.__file__}")

if __name__ == "__main__":
    port = 8000
    print(f"Starting ZeruScoreAgent on port {port}...")

    agent_instance = WrappedZeruScoreAgent()

    server = DefaultServer(agent_instance)

    server.run(port=port)
