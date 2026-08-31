from langchain_core.messages import HumanMessage, AIMessage
from state import AgentState


def agent_node(state: AgentState) -> dict:
    """
    Agent node that receives checkpointed state memory, extracts input and history,
    and returns updated messages to be persisted in short-term memory.
    """
    user_input = state.get("user_input", "")
    existing_messages = state.get("messages", [])
    
    # Calculate turn number from existing user messages stored in short-term memory
    user_msg_count = sum(
        1 for msg in existing_messages 
        if isinstance(msg, HumanMessage) or (isinstance(msg, dict) and msg.get("role") == "user")
    )
    turn = user_msg_count + 1

    # Formulate response referencing short-term memory context size
    history_count = len(existing_messages)
    agent_response = (
        f"[Memory Turn {turn}] Agent processed: '{user_input}' "
        f"| Short-term memory depth: {history_count} messages"
    )

    # Return new turn messages to be saved to short-term checkpointer memory
    new_messages = [
        HumanMessage(content=user_input),
        AIMessage(content=agent_response),
    ]

    return {
        "agent_response": agent_response,
        "messages": new_messages,
    }
