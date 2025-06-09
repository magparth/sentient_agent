# agent.py
from score_model import lookup_wallet_score
from memory import build_coala_memory
from usecase_handler import generate_response
from llm_utils import generate_llm_prompt, ask_llm


class ZeruScoreAgent:
    def perceive(self, wallet_address,use_case):
        memory = build_coala_memory(wallet_address,use_case)
        return {"wallet": wallet_address}, memory

    def reason(self, wallet_info, memory, use_case):
        score = float(lookup_wallet_score(wallet_info["wallet"]))
        response = generate_response(wallet_info["wallet"], score, memory, use_case)

        try:
            prompt = generate_llm_prompt(wallet_info["wallet"], score, memory, use_case)
            explanation = ask_llm(prompt)
        except Exception as e:
            explanation = f"(LLM unavailable) Default reasoning applied. Error: {str(e)}"

        response["llm_analysis"] = explanation
        return response

    def act(self, result):
        return result
