from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.agent import agent_node


def create_graph():
    """
    Constructs and compiles the workflow graph with short-term memory checkpointer:
    START -> agent -> END
    """
    workflow = StateGraph(AgentState)
    
    # Add agent node to graph
    workflow.add_node("agent", agent_node)
    
    # Define execution graph flow: START -> agent -> END
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    
    # Enable short-term memory via in-memory checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled graph application instance with memory checkpointer
app = create_graph()
