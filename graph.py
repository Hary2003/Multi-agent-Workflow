from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.supervisor import supervisor_node
from agents.fan_in import fan_in_node
from agents.evaluator import evaluator_node
from agents.optimizer import optimizer_node
from agents.approval import approval_node
from subgraphs import research_subgraph, planner_subgraph, coder_subgraph


def route_evaluator_decision(state: AgentState) -> str:
    """
    Conditional routing function for Evaluator node:
    - If is_good_enough is True -> route to 'approval_node' (Human-in-the-Loop Interrupt)
    - If is_good_enough is False -> route to 'optimizer'
    """
    if state.get("is_good_enough", False):
        return "approval_node"
    return "optimizer"


def create_graph():
    """
    Constructs and compiles the parallel multi-agent workflow graph:
    START -> SUPERVISOR -> (Fan-Out) -> [RESEARCH, PLANNER, CODER SUBGRAPHS] -> (Fan-In) -> FAN-IN -> EVALUATOR
                                                                                                        │
                                                                                                   [Good enough?]
                                                                                                   ├── YES → APPROVAL NODE (⏸ INTERRUPT) -> END
                                                                                                   └── NO  → OPTIMIZER -> EVALUATOR
    """
    workflow = StateGraph(AgentState)
    
    # Add supervisor and subgraph worker nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research_subgraph", research_subgraph)
    workflow.add_node("planner_subgraph", planner_subgraph)
    workflow.add_node("coder_subgraph", coder_subgraph)
    
    # Add Fan-In, Evaluator, Optimizer, and Approval nodes
    workflow.add_node("fan_in", fan_in_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("approval_node", approval_node)
    
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
    
    # Conditional Edge: Evaluator -> APPROVAL NODE (if good enough) or OPTIMIZER (if needs improvement)
    workflow.add_conditional_edges(
        "evaluator",
        route_evaluator_decision,
        {
            "approval_node": "approval_node",
            "optimizer": "optimizer"
        }
    )
    
    # Optimizer routes back to Evaluator for re-evaluation
    workflow.add_edge("optimizer", "evaluator")

    # Approval Node completes execution to END
    workflow.add_edge("approval_node", END)
    
    # Enable short-term memory via in-memory checkpointer & Human Interrupt before Approval Node
    checkpointer = MemorySaver()
    
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval_node"]
    )


# Export compiled graph application instance with memory checkpointer
app = create_graph()



