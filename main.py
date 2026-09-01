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

    # STAGE 2: Execute Graph (triggers nodes)
    output_state = app.invoke({"user_input": user_input}, config=config)

    # STAGE 3: Save Checkpoint to Thread Memory
    state_after = app.get_state(config)
    saved_messages = state_after.values.get("messages", [])
    print(f"  [3. Save Checkpoint] Saved state to thread '{thread_id}' (Total messages: {len(saved_messages)}).")
    print(f"  [Output Response]: '{output_state['agent_response']}'")

    return output_state


def main():
    print("=== Checkpointer invoke() Lifecycle Demonstration ===")
    print("Lifecycle Sequence: invoke() -> Load State -> Execute Graph -> Save Checkpoint\n")

    # Call 1: Thread 1 First Turn
    invoke_with_checkpoint_tracing("Hello, start session!", thread_id="session-101")

    # Call 2: Thread 1 Second Turn (demonstrates loading state, executing graph, saving new checkpoint)
    invoke_with_checkpoint_tracing("Remember my preference: Dark Mode.", thread_id="session-101")

    # Call 3: Thread 2 First Turn (demonstrates separate thread state loading)
    invoke_with_checkpoint_tracing("Hello from separate session!", thread_id="session-202")


if __name__ == "__main__":
    main()
