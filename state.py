from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


def keep_first(left: str, right: str) -> str:
    """Reducer that preserves the original non-empty value across parallel writes."""
    if left is not None and left != "":
        return left
    return right if right is not None else ""


def pick_last(left: str, right: str) -> str:
    """Reducer that accepts the latest updated value from parallel execution channels."""
    if right is not None and right != "":
        return right
    return left if left is not None else ""


class AgentState(TypedDict):
    user_input: Annotated[str, keep_first]
    agent_response: Annotated[str, pick_last]
    next_agent: Annotated[str, pick_last]
    # Research Subgraph state
    research_raw: Annotated[str, pick_last]
    research_analysis: Annotated[str, pick_last]
    research_output: Annotated[str, pick_last]
    # Planner Subgraph state
    planner_understanding: Annotated[str, pick_last]
    planner_breakdown: Annotated[str, pick_last]
    planner_output: Annotated[str, pick_last]
    # Coder Subgraph state
    coder_draft: Annotated[str, pick_last]
    coder_review: Annotated[str, pick_last]
    coder_output: Annotated[str, pick_last]
    # Orchestrator & Messages state
    final_response: Annotated[str, pick_last]
    messages: Annotated[list, add_messages]




