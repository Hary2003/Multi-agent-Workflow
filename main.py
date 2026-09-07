from graph import app


def invoke_with_checkpoint_tracing(user_input: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n=======================================================")
    print(f">> RUN: graph.invoke(user_input='{user_input}', thread_id='{thread_id}')")
    print(f"=======================================================")

    # STAGE 1: Execute graph until Approval Node interrupt
    initial_output = app.invoke({"user_input": user_input}, config=config)

    # Check state snapshot for human interrupt
    state_snapshot = app.get_state(config)
    next_nodes = list(state_snapshot.next) if state_snapshot.next else []

    if "approval_node" in next_nodes:
        print(f"\n  [[INTERRUPT] DETECTED] Workflow execution halted at: {next_nodes}")
        print("  [Human Reviewer Action] Simulating human approval submission...")

        # Update state with human approval decision
        app.update_state(
            config,
            {
                "is_approved": True,
                "approval_status": "approved",
                "approval_feedback": "CLI Reviewer approved the output.",
            }
        )

        # Resume graph execution from interrupt checkpoint
        final_output = app.invoke(None, config=config)
        print("\n  [Resume Completed] Graph execution completed after human approval.")
        state_after = app.get_state(config)
        print(f"  [Final Next Agent]: '{state_after.values.get('next_agent')}'")
        print(f"  [Approval Status]: '{state_after.values.get('approval_status')}'")
        print(f"  [Final Response Output]:\n{state_after.values.get('final_response')}")
        return final_output
    else:
        print(f"  [Completed without interrupt]: '{initial_output.get('agent_response')}'")
        return initial_output


def main():
    print("=== Fan-Out / Fan-In Parallel Multi-Agent Workflow Demonstration ===")
    print("Sequence: START -> Supervisor -> (Fan-Out) -> [Research, Planner, Coder] -> (Fan-In) -> Evaluator -> GOOD/BAD (Optimizer) -> APPROVAL NODE ([INTERRUPT]) -> END\n")

    invoke_with_checkpoint_tracing(
        "Design and implement a RAG-powered chatbot in Python",
        thread_id="session-fanin-101"
    )


if __name__ == "__main__":
    main()
