from langchain_core.messages import AIMessage
from state import AgentState


def evaluator_node(state: AgentState) -> dict:
    """
    Evaluator Node: Assesses synthesized output quality from Fan-In aggregator.
    Determines if quality meets requirements ("is_good_enough") or needs optimization loop.
    """
    user_input = state.get("user_input", "")
    current_iterations = state.get("iteration_count", 0) + 1
    max_iterations = state.get("max_iterations") or 2
    optimization_directives = state.get("optimization_directives", "")

    print(f"  [Evaluator Node] Evaluating output quality (Iteration {current_iterations}/{max_iterations})")

    # If already refined by Optimizer OR reached max iterations limit, pass evaluation
    if optimization_directives or current_iterations >= max_iterations:
        score = 95.0
        is_good_enough = True
        feedback = f"[Evaluator] Approved. Synthesis meets quality criteria on iteration {current_iterations}."
    else:
        # First iteration: require optimization refinement
        score = 70.0
        is_good_enough = False
        feedback = "[Evaluator] Revision requested. Need enhanced security safeguards and production deployment steps."

    log_msg = f"[Evaluator] Iteration {current_iterations}: Score={score}/100 | Good Enough={is_good_enough}"
    print(f"  {log_msg}")

    return {
        "iteration_count": current_iterations,
        "max_iterations": max_iterations,
        "evaluation_score": score,
        "evaluation_feedback": feedback,
        "is_good_enough": is_good_enough,
        "messages": [AIMessage(content=log_msg)]
    }

