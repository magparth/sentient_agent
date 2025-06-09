# query_parser.py

import re

def parse_query(prompt: str):
    prompt = prompt.lower()

    # Extract wallet address
    wallet_match = re.search(r"0x[a-f0-9]{40}", prompt)
    wallet = wallet_match.group(0) if wallet_match else None

    # Heuristic for use case
    if "loan" in prompt or "collateral" in prompt:
        use_case = "loan"
    elif "airdrop" in prompt or "mint" in prompt:
        use_case = "airdrop"
    elif "governance" in prompt or "vote" in prompt:
        use_case = "governance"
    else:
        use_case = "default"

    return wallet, use_case
