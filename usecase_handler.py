# usecase_handler.py

def generate_response(wallet, score, memory, use_case):
    score = float(score)  # Ensure proper numeric comparisons
    # print(f"DEBUG — Wallet: {wallet}, Score: {score}")

    # Tier assignment
    if score >= 850:
        label = "Tier A"
    elif score >= 650:
        label = "Tier B"
    elif score >= 400:
        label = "Tier C"
    else:
        label = "Tier D"

    if use_case == "loan":
        if label == "Tier A":
            loan_limit = "$50K"
            interest_rate = "5.5%"
        elif label == "Tier B":
            loan_limit = "$25K"
            interest_rate = "8%"
        elif label == "Tier C":
            loan_limit = "$10K"
            interest_rate = "12%"
        else:
            loan_limit = "$0"
            interest_rate = "N/A"

        return {
            "wallet": wallet,
            "zScore": score,
            "use_case": "loan",
            "tier": label,
            "terms": {
                "loan_limit": loan_limit,
                "interest_rate": interest_rate,
                "rationale": memory["semantic"][0] if memory["semantic"] else "Behavior-based evaluation"
            },
            "memory": memory
        }

    elif use_case == "airdrop":
        eligible = label in ["Tier A", "Tier B"]
        return {
            "wallet": wallet,
            "zScore": score,
            "use_case": "airdrop_eligibility",
            "eligible": eligible,
            "reason": f"Wallet is {label}, which {'qualifies' if eligible else 'does not qualify'} for airdrop",
            "memory": memory
        }

    elif use_case == "governance":
        weight = 3 if label == "Tier A" else 2 if label == "Tier B" else 1
        return {
            "wallet": wallet,
            "zScore": score,
            "use_case": "governance_voting",
            "voting_power": weight,
            "label": label,
            "memory": memory
        }

    else:
        return {
            "wallet": wallet,
            "zScore": score,
            "label": label,
            "memory": memory
        }
