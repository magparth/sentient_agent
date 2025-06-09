import pandas as pd
from datetime import datetime

def build_coala_memory(wallet, use_case="default"):
    wallet = wallet.lower()

    deposits = pd.read_csv('deposits.csv')
    withdraws = pd.read_csv('withdraws.csv')
    swaps = pd.read_csv('swaps.csv')

    dep = deposits[deposits['account_id'].str.lower() == wallet]
    wth = withdraws[withdraws['account_id'].str.lower() == wallet]
    swp = swaps[swaps['account_id'].str.lower() == wallet]

    # Procedural memory
    procedural = []
    if not dep.empty:
        procedural.append("Provides liquidity")
    if not wth.empty:
        procedural.append("Withdraws periodically")
    if not swp.empty:
        procedural.append("Swaps assets across pools")

    # Semantic memory
    semantic = [
        "Wallet is active across multiple DeFi operations (deposits, swaps, withdraws).",
        "Could be engaged in yield farming or liquidity provision."
    ]

    # Episodic memory — filtered per use_case
    episodic = []

    if use_case == "loan":
        for _, row in dep.sort_values("amountUSD", ascending=False).head(3).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Deposited ${round(row['amountUSD'], 2)}"})

        for _, row in wth.sort_values("timestamp", ascending=False).head(2).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Withdrew ${round(row['amountUSD'], 2)}"})

    elif use_case == "airdrop":
        for _, row in swp.head(3).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Swapped {row['tokenIn_symbol']} → {row['tokenOut_symbol']}"})

    elif use_case == "governance":
        for _, row in dep.head(3).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Staked ${round(row['amountUSD'], 2)}"})

    else:
        # default fallback (mixed view)
        for _, row in dep.head(2).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Deposited ${round(row['amountUSD'], 2)}"})

        for _, row in swp.head(1).iterrows():
            dt = pd.to_datetime(row['timestamp'], unit='s', errors='coerce')
            episodic.append({"date": dt.strftime('%Y-%m-%d'), "event": f"Swapped {row['tokenIn_symbol']} → {row['tokenOut_symbol']}"})

    return {
        "procedural": procedural,
        "semantic": semantic,
        "episodic": episodic
    }
