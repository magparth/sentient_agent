# wrapped_agent.py

import sys
import os
import json

# Add local Sentient framework path (adjust as needed for your directory)
sys.path.append(os.path.abspath("../Sentient-Agent-Framework-main/Sentient-Agent-Framework-main/src"))

from querry_parser import parse_query
from agent import ZeruScoreAgent
from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.session import Session
from sentient_agent_framework.interface.request import Query
from sentient_agent_framework.interface.response_handler import ResponseHandler
from sentient_agent_framework.interface.events import TextBlockEvent, EventContentType, DoneEvent

class WrappedZeruScoreAgent(AbstractAgent):
    def __init__(self, name="ZeruScoreAgent"):
        super().__init__(name)
        self.core_agent = ZeruScoreAgent()

    async def assist(self, session: Session, query: Query, response_handler: ResponseHandler):
        try:
            print("👉 WrappedZeruScoreAgent.assist() called.")  # Debug

            prompt_text = query.prompt.strip()
            print(f"👉 Received prompt: {prompt_text}")  # Debug

            wallet, use_case = parse_query(prompt_text)
            print(f"👉 Parsed wallet: {wallet}, use_case: {use_case}")  # Debug

            if not wallet:
                print("👉 No wallet found — sending error response.")  # Debug
                await response_handler._hook.emit(TextBlockEvent(
                    content_type=EventContentType.TEXTBLOCK,
                    event_name="ZeruScoreResponse",
                    source=response_handler._source.id,
                    content="❌ Error: Wallet address not found in query.",
                    stream_id="default",
                    is_complete=False
                ))
                await response_handler._hook.emit(DoneEvent(
                    source=response_handler._source.id
                ))
                return

            # Agent pipeline
            print("👉 Calling self.core_agent.perceive()")  # Debug
            perception, memory = self.core_agent.perceive(wallet, use_case)

            print("👉 Calling self.core_agent.reason()")  # Debug
            decision = self.core_agent.reason(perception, memory, use_case)

            print("👉 Calling self.core_agent.act()")  # Debug
            result = self.core_agent.act(decision)

            # Extract only llm_analysis
            llm_summary = result.get("llm_analysis", "❌ No analysis generated.")
            print(f"👉 Final llm_analysis to emit:\n{llm_summary}")  # Debug

            # Stream only llm_analysis
            await response_handler._hook.emit(TextBlockEvent(
                content_type=EventContentType.TEXTBLOCK,
                event_name="ZeruScoreResponse",
                source=response_handler._source.id,
                content=llm_summary,
                stream_id="default",
                is_complete=False
            ))

            await response_handler._hook.emit(DoneEvent(
                source=response_handler._source.id
            ))

        except Exception as e:
            print(f"❌ Agent failed with exception: {str(e)}")  # Debug

            await response_handler._hook.emit(TextBlockEvent(
                content_type=EventContentType.TEXTBLOCK,
                event_name="ZeruScoreResponse",
                source=response_handler._source.id,
                content=f"❌ Agent failed: {str(e)}",
                stream_id="default",
                is_complete=False
            ))
            await response_handler._hook.emit(DoneEvent(
                source=response_handler._source.id
            ))
