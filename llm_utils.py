import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def generate_llm_prompt(wallet, score, memory, use_case):
    return f"""
You are a DeFi reputation analyst agent.

Wallet Address: {wallet}
zScore: {score} (Range: 0–1000, where higher scores indicate stronger trustworthiness)

Use Case: {use_case.upper()}

# Semantic Knowledge (General Traits):
{chr(10).join(memory.get('semantic', []))}

# Procedural Behavior (Behavior Patterns):
{chr(10).join(memory.get('procedural', []))}

# Episodic Memory (Historical Events):
{chr(10).join([f"{e['date']}: {e['event']}" for e in memory.get('episodic', [])])}

Instructions:
1. Analyze the episodic memory to identify repayment frequency, loan reliability, or suspicious behavior.
2. Combine it with procedural and semantic memory to assess if the user qualifies for the selected use case.
3. Base your decision on both the behavior and zScore value.

Return a 2–3 sentence explanation suitable for a DAO credit officer.
"""


def ask_llm(prompt):
    headers = { "Content-Type": "application/json" }
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(URL, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
