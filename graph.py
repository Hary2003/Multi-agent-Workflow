from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node
from agents.worker_agents import researcher_node, planner_node, coder_node


def route_supervisor(state: AgentState) -> str:
    """
    Conditional edge router that checks the supervisor's decision in state.
    """
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent


def create_graph():
    """
    Constructs and compiles the multi-agent workflow graph with a supervisor node:
    START -> supervisor -> conditional_edge -> (researcher / planner / coder) -> supervisor -> END
    """
    workflow = StateGraph(AgentState)
    
    # Add supervisor and worker nodes to graph
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    
    # Execution starts at supervisor node
    workflow.add_edge(START, "supervisor")
    
    # Conditional routing from supervisor to worker agents or END
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "planner": "planner",
            "coder": "coder",
            END: END,
        }
    )
    
    # Worker nodes return execution back to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("coder", "supervisor")

    
    # Enable short-term memory via in-memory checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled graph application instance with memory checkpointer
app = create_graph()
