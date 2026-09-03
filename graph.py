from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node
from agents.fan_in import fan_in_node
from subgraphs import research_subgraph, planner_subgraph, coder_subgraph


def create_graph():
    """
    Constructs and compiles the parallel multi-agent workflow graph:
    START -> SUPERVISOR -> (Fan-Out) -> [RESEARCH SUBGRAPH, PLANNER SUBGRAPH, CODER SUBGRAPH] -> (Fan-In) -> FAN-IN -> END
    """
    workflow = StateGraph(AgentState)
    
    # Add supervisor node
    workflow.add_node("supervisor", supervisor_node)
    
    # Add compiled subgraphs as graph nodes (Parallel Fan-Out execution branches)
    workflow.add_node("research_subgraph", research_subgraph)
    workflow.add_node("planner_subgraph", planner_subgraph)
    workflow.add_node("coder_subgraph", coder_subgraph)
    
    # Add Fan-In aggregator node
    workflow.add_node("fan_in", fan_in_node)
    
    # Execution starts at supervisor node
    workflow.add_edge(START, "supervisor")
    
    # Fan-Out: Supervisor dispatches to Research, Planner, and Coder subgraphs in parallel
    workflow.add_edge("supervisor", "research_subgraph")
    workflow.add_edge("supervisor", "planner_subgraph")
    workflow.add_edge("supervisor", "coder_subgraph")
    
    # Fan-In: All three subgraphs feed into the fan_in aggregator node
    workflow.add_edge("research_subgraph", "fan_in")
    workflow.add_edge("planner_subgraph", "fan_in")
    workflow.add_edge("coder_subgraph", "fan_in")
    
    # Fan-In aggregator completes the graph workflow
    workflow.add_edge("fan_in", END)
    
    # Enable short-term memory via in-memory checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled graph application instance with memory checkpointer
app = create_graph()


