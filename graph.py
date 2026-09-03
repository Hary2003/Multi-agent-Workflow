from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node
from agents.fan_in import fan_in_node
from agents.evaluator import evaluator_node
from agents.optimizer import optimizer_node
from subgraphs import research_subgraph, planner_subgraph, coder_subgraph


def route_evaluator_decision(state: AgentState) -> str:
    """
    Conditional routing function for Evaluator node:
    - If is_good_enough is True -> route to END
    - If is_good_enough is False -> route to 'optimizer'
    """
    if state.get("is_good_enough", False):
        return END
    return "optimizer"


def create_graph():
    """
    Constructs and compiles the parallel multi-agent workflow graph:
    START -> SUPERVISOR -> (Fan-Out) -> [RESEARCH, PLANNER, CODER SUBGRAPHS] -> (Fan-In) -> FAN-IN -> EVALUATOR
                                                                                                        │
                                                                                                  [Good enough?]
                                                                                                  ├── YES → END
                                                                                                  └── NO → OPTIMIZER -> SUPERVISOR
    """
    workflow = StateGraph(AgentState)
    
    # Add supervisor and subgraph worker nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research_subgraph", research_subgraph)
    workflow.add_node("planner_subgraph", planner_subgraph)
    workflow.add_node("coder_subgraph", coder_subgraph)
    
    # Add Fan-In, Evaluator, and Optimizer nodes
    workflow.add_node("fan_in", fan_in_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("optimizer", optimizer_node)
    
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
    
    # Fan-In aggregator feeds into Evaluator node
    workflow.add_edge("fan_in", "evaluator")
    
    # Conditional Edge: Evaluator -> END (if good enough) or OPTIMIZER (if needs improvement)
    workflow.add_conditional_edges(
        "evaluator",
        route_evaluator_decision,
        {
            END: END,
            "optimizer": "optimizer"
        }
    )
    
    # Optimizer routes back to Supervisor for Re-run / Improve pass
    workflow.add_edge("optimizer", "supervisor")
    
    # Enable short-term memory via in-memory checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled graph application instance with memory checkpointer
app = create_graph()



