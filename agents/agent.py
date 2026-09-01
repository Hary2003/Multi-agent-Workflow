from langchain_core.messages import HumanMessage, AIMessage
from state import AgentState


def agent_node(state: AgentState) -> dict:
    """
    Agent node that receives state loaded from checkpointer, executes logic,
    and returns updated messages to be saved back to checkpointer memory.
    """
    user_input = state.get("user_input", "")
    existing_messages = state.get("messages", [])
    
    print(f"  [2. Execute Graph] Node 'agent' running with input: '{user_input}' (Prior history: {len(existing_messages)} msgs)")

    user_msg_count = sum(
        1 for msg in existing_messages 
        if isinstance(msg, HumanMessage) or (isinstance(msg, dict) and msg.get("role") == "user")
    )
    turn = user_msg_count + 1

    agent_response = (
        f"[Turn {turn}] Processed '{user_input}' successfully."
    )

    new_messages = [
        HumanMessage(content=user_input),
        AIMessage(content=agent_response),
    ]

    return {
        "agent_response": agent_response,
        "messages": new_messages,
    }
