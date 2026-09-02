from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node
from agents.worker_agents import researcher_node, planner_node, coder_node
from agents.fan_in import fan_in_node


def create_graph():
    """
    Constructs and compiles the parallel multi-agent workflow graph:
    START -> supervisor -> (Fan-Out) -> [researcher, planner, coder] -> (Fan-In) -> fan_in -> END
    """
    workflow = StateGraph(AgentState)
    
    # Add supervisor, worker nodes, and fan_in aggregator node to graph
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("fan_in", fan_in_node)
    
    # Execution starts at supervisor node
    workflow.add_edge(START, "supervisor")
    
    # Fan-Out: Supervisor triggers researcher, planner, and coder in parallel branches
    workflow.add_edge("supervisor", "researcher")
    workflow.add_edge("supervisor", "planner")
    workflow.add_edge("supervisor", "coder")
    
    # Fan-In: All three worker nodes feed into the fan_in aggregator node
    workflow.add_edge("researcher", "fan_in")
    workflow.add_edge("planner", "fan_in")
    workflow.add_edge("coder", "fan_in")
    
    # Fan-In aggregator completes the graph workflow
    workflow.add_edge("fan_in", END)
    
    # Enable short-term memory via in-memory checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled graph application instance with memory checkpointer
app = create_graph()

