import asyncio
import ulid
from wrapped_agent import WrappedZeruScoreAgent
from sentient_agent_framework.interface.request import Query
from sentient_agent_framework.interface.response_handler import ResponseHandler

class MockSession:
    def __init__(self, user_id="test", memory=None):
        self.user_id = user_id
        self.memory = memory or {}

class MockResponseHandler(ResponseHandler):
    async def stream(self, message):
        print("--- Wrapped Agent Output ---")
        print(message)

async def run_agent():
    agent = WrappedZeruScoreAgent()
    session = MockSession()

    # ✅ Natural language prompt example
    prompt = "Is 0xe0b763ad8b0387d0a3b0a2d8fb7cd5fd0b14fb8a eligible for a $10K loan?"

    query = Query(
        id=str(ulid.ULID()),  # Correct ULID format
        prompt=prompt
    )

    response_handler = MockResponseHandler()
    await agent.assist(session, query, response_handler)

asyncio.run(run_agent())
