from langchain_core.messages import BaseMessage
from graph import app


def run_checkpoint_memory_demo():
    print("=== Phase 3: Short-Term Memory (Checkpointer) Workflow ===")

    # Thread configurations for short-term memory isolation
    config_thread_1 = {"configurable": {"thread_id": "thread-1"}}
    config_thread_2 = {"configurable": {"thread_id": "thread-2"}}

    print("\n--- Executing Thread 1 (Turn 1) ---")
    res1 = app.invoke({"user_input": "Hello from Thread 1!"}, config=config_thread_1)
    print(f"Response: {res1['agent_response']}")

    print("\n--- Executing Thread 1 (Turn 2) ---")
    res2 = app.invoke({"user_input": "Remember my key code is 9982."}, config=config_thread_1)
    print(f"Response: {res2['agent_response']}")

    print("\n--- Executing Thread 2 (Turn 1 - Isolated Memory) ---")
    res3 = app.invoke({"user_input": "Hello from Thread 2!"}, config=config_thread_2)
    print(f"Response: {res3['agent_response']}")

    # Retrieve short-term checkpoint state for Thread 1
    state_t1 = app.get_state(config_thread_1)
    print("\n=== Retrieved Memory for [thread-1] ===")
    for msg in state_t1.values.get("messages", []):
        role = msg.type.upper() if isinstance(msg, BaseMessage) else "UNKNOWN"
        print(f"[{role}]: {msg.content}")

    # Retrieve short-term checkpoint state for Thread 2
    state_t2 = app.get_state(config_thread_2)
    print("\n=== Retrieved Memory for [thread-2] ===")
    for msg in state_t2.values.get("messages", []):
        role = msg.type.upper() if isinstance(msg, BaseMessage) else "UNKNOWN"
        print(f"[{role}]: {msg.content}")


if __name__ == "__main__":
    run_checkpoint_memory_demo()
