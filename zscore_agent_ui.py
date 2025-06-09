import streamlit as st
import json
import asyncio
import ulid

from wrapped_agent import WrappedZeruScoreAgent
from sentient_agent_framework.interface.request import Query
from sentient_agent_framework.interface.response_handler import ResponseHandler

# ✅ Mock session to comply with AbstractAgent
class MockSession:
    def __init__(self, user_id="streamlit-user", memory=None):
        self.user_id = user_id
        self.memory = memory or {}

# Streamlit UI setup
st.set_page_config(page_title="zScore Agent", layout="centered")
st.title("🔍 zScore Reputation Agent")
st.markdown("Type your natural language prompt ")

user_prompt = st.text_area("Prompt", placeholder="e.g., Is 0xabc... eligible for an airdrop?")

result_placeholder = st.empty()

if st.button("Submit"):
    if not user_prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        async def run_agent():
            class StreamlitResponseHandler(ResponseHandler):
                async def stream(self, message):
                    try:
                        parsed = json.loads(message)
                        llm_text = parsed.get("llm_analysis", "No LLM analysis available.")
                        result_placeholder.markdown(f"**🧠 LLM Analysis:**\n\n{llm_text}")
                    except:
                        result_placeholder.text(message)

            agent = WrappedZeruScoreAgent()
            session = MockSession()
            query = Query(id=str(ulid.ULID()), prompt=user_prompt)
            response_handler = StreamlitResponseHandler()
            await agent.assist(session, query, response_handler)

        asyncio.run(run_agent())
