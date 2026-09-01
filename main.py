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
    print("=== Supervisor Multi-Agent Workflow Demonstration ===")
    print("Lifecycle Sequence: invoke() -> Load State -> Supervisor Node -> Worker Node -> Supervisor Node -> Save Checkpoint\n")

    # Call 1: Research task (Thread session-101)
    invoke_with_checkpoint_tracing("Please research quantum computing breakthroughs.", thread_id="session-101")

    # Call 2: Coding task (Thread session-101)
    invoke_with_checkpoint_tracing("Write a Python script to sort a binary tree.", thread_id="session-101")

    # Call 3: Finish/Exit task (Thread session-202)
    invoke_with_checkpoint_tracing("We are all done with session 202, please finish.", thread_id="session-202")


if __name__ == "__main__":
    main()
