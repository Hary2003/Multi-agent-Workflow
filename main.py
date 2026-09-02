from graph import app


def invoke_with_checkpoint_tracing(user_input: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n=======================================================")
    print(f">> CALL: checkpointer.invoke(user_input='{user_input}', thread_id='{thread_id}')")
    print(f"=======================================================")

    # STAGE 1: Load State from Checkpointer Memory
    state_before = app.get_state(config)
    prior_messages = state_before.values.get("messages", [])
    print(f"  [1. Load State] Loaded {len(prior_messages)} prior messages from thread '{thread_id}'.")

    # STAGE 2: Execute Graph (triggers supervisor & worker nodes)
    output_state = app.invoke({"user_input": user_input, "next_agent": None}, config=config)


    # STAGE 3: Save Checkpoint to Thread Memory
    state_after = app.get_state(config)
    saved_messages = state_after.values.get("messages", [])
    print(f"  [3. Save Checkpoint] Saved state to thread '{thread_id}' (Total messages: {len(saved_messages)}).")
    print(f"  [Final Next Agent]: '{output_state.get('next_agent')}'")
    print(f"  [Output Response]: '{output_state.get('agent_response')}'")

    return output_state


def main():
    print("=== Fan-Out / Fan-In Parallel Multi-Agent Workflow Demonstration ===")
    print("Lifecycle Sequence: START -> Supervisor -> (Fan-Out) -> [Research, Planner, Coder] -> (Fan-In) -> Aggregator -> END\n")

    # Run Fan-Out / Fan-In workflow on a composite task
    invoke_with_checkpoint_tracing(
        "Design and implement a RAG-powered chatbot in Python",
        thread_id="session-fanin-101"
    )


if __name__ == "__main__":
    main()


