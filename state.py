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


def pick_last_int(left: int, right: int) -> int:
    return right if right is not None else (left if left is not None else 0)


def pick_last_bool(left: bool, right: bool) -> bool:
    return right if right is not None else (left if left is not None else False)


def pick_last_float(left: float, right: float) -> float:
    return right if right is not None else (left if left is not None else 0.0)


def keep_first_int(left: int, right: int) -> int:
    if left is not None and left > 0:
        return left
    if right is not None and right > 0:
        return right
    return 2



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
    # Evaluator & Optimizer state
    evaluation_score: Annotated[float, pick_last_float]
    evaluation_feedback: Annotated[str, pick_last]
    is_good_enough: Annotated[bool, pick_last_bool]
    iteration_count: Annotated[int, pick_last_int]
    max_iterations: Annotated[int, keep_first_int]
    optimization_directives: Annotated[str, pick_last]
    # Approval Node state
    approval_status: Annotated[str, pick_last]
    approval_feedback: Annotated[str, pick_last]
    is_approved: Annotated[bool, pick_last_bool]
    # Orchestrator & Messages state
    final_response: Annotated[str, pick_last]
    messages: Annotated[list, add_messages]





