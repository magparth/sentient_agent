
import pandas as pd
from datetime import datetime

def lookup_wallet_score(wallet_address: str) -> float:
    wallet_address = wallet_address.lower()

    try:
        deposits = pd.read_csv('deposits.csv')
        withdraws = pd.read_csv('withdraws.csv')
        swaps = pd.read_csv('swaps.csv')

        deposits['datetime'] = pd.to_datetime(deposits['timestamp'], unit='s')
        withdraws['datetime'] = pd.to_datetime(withdraws['timestamp'], unit='s')
        swaps['datetime'] = pd.to_datetime(swaps['timestamp'], unit='s')

        # Time Score
        all_events = pd.concat([
            deposits[['account_id', 'datetime']],
            withdraws[['account_id', 'datetime']],
            swaps[['account_id', 'datetime']]
        ])
        filtered = all_events[all_events['account_id'].str.lower() == wallet_address]
        if filtered.empty:
            return 0.0

        first_tx = filtered['datetime'].min()
        days_active = (datetime.utcnow() - first_tx).days

        def compute_time_score(days):
            score = 20
            if days >= 7: score += 10
            if days >= 30: score += 15
            if days >= 90: score += 15
            if days >= 180: score += 20
            if days >= 365: score += 10
            if days > 365: score += 10
            return min(score, 100)

        time_score = compute_time_score(days_active)

        # Filter wallet-specific records
        user_deposits = deposits[deposits['account_id'].str.lower() == wallet_address].copy()
        user_withdraws = withdraws[withdraws['account_id'].str.lower() == wallet_address].copy()
        user_swaps = swaps[swaps['account_id'].str.lower() == wallet_address].copy()

        # --- Deposit Score ---
        deposit_score = 0
        bot_score = 125
        if not user_deposits.empty:
            withdraw_info = user_withdraws[['datetime', 'amountUSD']].copy()
            withdraw_info.rename(columns={'datetime': 'datetime_withdraw', 'amountUSD': 'amountUSD_withdraw'}, inplace=True)

            merged = pd.merge(
                user_deposits[['datetime', 'amountUSD']],
                withdraw_info,
                how='left',
                left_index=True,
                right_index=True
            )
            merged['time_diff'] = (merged['datetime_withdraw'] - merged['datetime']).dt.total_seconds()
            merged['value_diff'] = abs(merged['amountUSD_withdraw'] - merged['amountUSD']) / merged['amountUSD']
            merged['is_bot'] = (merged['time_diff'] >= 0) & (merged['time_diff'] <= 60) & (merged['value_diff'] <= 0.02)

            user_deposits['is_bot'] = merged['is_bot'].fillna(False)
            user_deposits['effective_amountUSD'] = user_deposits.apply(
                lambda row: row['amountUSD'] * 0.1 if row['is_bot'] else row['amountUSD'], axis=1
            )
            total_volume = user_deposits['effective_amountUSD'].sum()

            def volume_score(amount):
                if amount >= 100000: return 250
                elif amount >= 50000: return 200
                elif amount >= 10000: return 150
                elif amount >= 1000: return 100
                elif amount >= 100: return 50
                else: return 20

            volume_component = volume_score(total_volume)

            user_deposits['day'] = user_deposits['datetime'].dt.date
            user_deposits['day_weight'] = user_deposits['is_bot'].apply(lambda x: 0.2 if x else 1.0)

            active_days = user_deposits.groupby('day')['day_weight'].max().sum()
            months_active = max((user_deposits['datetime'].max() - user_deposits['datetime'].min()).days / 30, 1)
            avg_monthly_days = active_days / months_active

            def frequency_score(avg):
                if avg >= 8: return 125
                elif avg >= 4: return 100
                elif avg >= 2: return 75
                elif avg >= 1: return 50
                else: return 25

            freq_component = frequency_score(avg_monthly_days)
            num_bot_deposits = user_deposits['is_bot'].sum()

            def compute_bot_score(n):
                if n == 0: return 125
                elif n <= 3: return 112.5
                elif n <= 10: return 100
                elif n <= 50: return 50
                else: return 0

            bot_score = compute_bot_score(num_bot_deposits)
            deposit_score = volume_component + freq_component + bot_score

        # --- Withdraw Score ---
        withdraw_score = 200  # default
        if not user_withdraws.empty and not user_deposits.empty:
            deposits_sorted = user_deposits.sort_values(by='datetime')
            withdraws_sorted = user_withdraws.sort_values(by='datetime')
            hold_times = []
            d_idx = 0
            d_times = deposits_sorted['datetime'].tolist()
            w_times = withdraws_sorted['datetime'].tolist()

            for w in w_times:
                while d_idx < len(d_times) and d_times[d_idx] <= w:
                    d_idx += 1
                if d_idx == 0: continue
                hold = (w - d_times[d_idx - 1]).total_seconds() / (60 * 60 * 24)
                hold_times.append(hold)

            avg_hold_days = sum(hold_times) / len(hold_times) if hold_times else 0

            def holding_time_score(days):
                if days >= 90: return 120
                elif days >= 30: return 90
                elif days >= 7: return 60
                elif days >= 1: return 30
                elif days >= (1 / 24): return 10
                else: return 1

            hold_score = holding_time_score(avg_hold_days)
            withdraw_ratio = len(withdraws_sorted) / max(len(deposits_sorted), 1)

            def withdrawal_frequency_score(ratio):
                if ratio <= 0.1: return 80
                elif ratio <= 0.3: return 60
                elif ratio <= 0.6: return 40
                elif ratio <= 1.0: return 20
                else: return 5

            freq_score = withdrawal_frequency_score(withdraw_ratio)
            withdraw_score = hold_score + freq_score

        # --- Swap Score ---
        swap_score = 0
        if not user_swaps.empty:
            user_swaps['fee_usd'] = (user_swaps['amountOutUSD'] - user_swaps['amountInUSD']).clip(lower=0)
            total_fee = user_swaps['fee_usd'].sum()

            def fee_volume_score(fee):
                if fee >= 1_000_000: return 120
                elif fee >= 500_000: return 100
                elif fee >= 100_000: return 80
                elif fee >= 10_000: return 40
                elif fee > 0: return 20
                else: return 0

            fee_component = fee_volume_score(total_fee)
            user_swaps['month'] = user_swaps['datetime'].dt.to_period('M')
            active_months = user_swaps['month'].nunique()

            def activity_score(months):
                if months >= 12: return 80
                elif months >= 6: return 60
                elif months >= 3: return 40
                elif months >= 1: return 20
                else: return 0

            activity_component = activity_score(active_months)
            swap_score = fee_component + activity_component

        total_score = round(time_score + deposit_score + withdraw_score + swap_score, 2)
        return total_score

    except Exception as e:
        print(f"[Wallet Scoring Error]: {e}")
        return 0.0
