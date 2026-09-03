from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from state import AgentState


def understand_step(state: AgentState) -> dict:
    """Stage 1: Understand - Deconstruct objectives, scope, and technical constraints."""
    user_input = state.get("user_input", "")
    print(f"    [Planner Subgraph -> 1. Understand] Analyzing goals and boundaries for: '{user_input}'")
    understanding = f"[Planner Scope] Objective parsed: '{user_input}'. Core focus: high availability and modular design."
    return {"planner_understanding": understanding}


def breakdown_step(state: AgentState) -> dict:
    """Stage 2: Break down - Divide objectives into functional execution phases."""
    user_input = state.get("user_input", "")
    understanding = state.get("planner_understanding", "")
    print(f"    [Planner Subgraph -> 2. Break down] Modularizing architecture for: '{user_input}'")
    breakdown = f"[Planner Breakdown] Component phases defined based on: '{understanding}'"
    return {"planner_breakdown": breakdown}


def create_plan_step(state: AgentState) -> dict:
    """Stage 3: Create Plan - Synthesize full actionable plan and roadmap."""
    user_input = state.get("user_input", "")
    breakdown = state.get("planner_breakdown", "")
    print(f"    [Planner Subgraph -> 3. Create plan] Finalizing implementation roadmap for: '{user_input}'")
    plan = (
        f"[Planner Subgraph Output]\n"
        f"• Task: '{user_input}'\n"
        f"• Structure: {breakdown}\n"
        f"• Action Plan: Step 1: Environment Setup -> Step 2: Core Logic Implementation -> Step 3: Testing & Deployment."
    )
    return {
        "planner_output": plan,
        "messages": [AIMessage(content=plan)]
    }


def create_planner_subgraph():
    """Builds and compiles the Planner Subgraph pipeline."""
    builder = StateGraph(AgentState)
    builder.add_node("understand", understand_step)
    builder.add_node("break_down", breakdown_step)
    builder.add_node("create_plan", create_plan_step)

    builder.add_edge(START, "understand")
    builder.add_edge("understand", "break_down")
    builder.add_edge("break_down", "create_plan")
    builder.add_edge("create_plan", END)

    return builder.compile()


planner_subgraph = create_planner_subgraph()
