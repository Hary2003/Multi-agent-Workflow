from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    user_input: str
    agent_response: str
    next_agent: str
    research_output: str
    planner_output: str
    coder_output: str
    final_response: str
    messages: Annotated[list, add_messages]


