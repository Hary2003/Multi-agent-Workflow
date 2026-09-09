import os
import json
import time
import uvicorn
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from graph import app as graph_app


SESSION_REGISTRY_FILE = "sessions.json"


def load_sessions() -> Dict[str, Any]:
    if os.path.exists(SESSION_REGISTRY_FILE):
        try:
            with open(SESSION_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_session(thread_id: str, prompt: str, is_interrupted: bool, next_node: Optional[str], final_state: Dict[str, Any]):
    sessions = load_sessions()
    sessions[thread_id] = {
        "thread_id": thread_id,
        "user_input": prompt,
        "is_interrupted": is_interrupted,
        "next_node": next_node,
        "approval_status": final_state.get("approval_status", ""),
        "evaluation_score": final_state.get("evaluation_score", 0.0),
        "iteration_count": final_state.get("iteration_count", 0),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "final_response": final_state.get("final_response", "") or final_state.get("agent_response", "")
    }
    try:
        with open(SESSION_REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"Error saving session metadata: {e}")


server = FastAPI(
    title="Persistent Multi-Agent Workflow API",
    description="FastAPI backend serving the LangGraph parallel multi-agent graph with subgraphs and Evaluator-Optimizer loop.",
    version="1.1.0"
)

# Enable CORS for local web development
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    user_input: str
    thread_id: Optional[str] = "session-demo-1"


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: Optional[str] = ""


@server.get("/api/health")
def health_check():
    return {"status": "online", "message": "Multi-Agent Workflow Engine Operational"}


@server.get("/api/threads")
def list_threads():
    sessions = load_sessions()
    return {"threads": list(sessions.values())}



@server.post("/api/run")
def run_workflow(request: WorkflowRequest):
    if not request.user_input or not request.user_input.strip():
        raise HTTPException(status_code=400, detail="User input cannot be empty.")
    
    thread_id = request.thread_id or "session-demo-1"
    config = {"configurable": {"thread_id": thread_id}}
    
    trajectory: List[Dict[str, Any]] = []
    
    try:
        # Stream step-by-step graph execution
        for event in graph_app.stream({"user_input": request.user_input}, config=config):
            if isinstance(event, dict):
                items = event.items()
            elif isinstance(event, tuple) and len(event) == 2 and isinstance(event[0], str):
                items = [(event[0], event[1])]
            else:
                items = []

            for node_name, node_state in items:
                if isinstance(node_state, dict):
                    trajectory.append({
                        "node": node_name,
                        "state_update": {
                            k: v for k, v in node_state.items() 
                            if k != "messages" # Messages format handled separately
                        }
                    })
        
        # Get state snapshot to check for interrupt
        state_snapshot = graph_app.get_state(config)
        final_state = state_snapshot.values
        next_nodes = list(state_snapshot.next) if state_snapshot.next else []
        is_interrupted = bool(next_nodes) and "approval_node" in next_nodes
        
        res_payload = {
            "success": True,
            "thread_id": thread_id,
            "user_input": request.user_input,
            "is_interrupted": is_interrupted,
            "next_node": next_nodes[0] if next_nodes else None,
            "trajectory": trajectory,
            "final_state": {
                "user_input": final_state.get("user_input", ""),
                "agent_response": final_state.get("agent_response", ""),
                "research_analysis": final_state.get("research_analysis", ""),
                "research_output": final_state.get("research_output", ""),
                "planner_breakdown": final_state.get("planner_breakdown", ""),
                "planner_output": final_state.get("planner_output", ""),
                "coder_review": final_state.get("coder_review", ""),
                "coder_output": final_state.get("coder_output", ""),
                "evaluation_score": final_state.get("evaluation_score", 0.0),
                "evaluation_feedback": final_state.get("evaluation_feedback", ""),
                "is_good_enough": final_state.get("is_good_enough", False),
                "iteration_count": final_state.get("iteration_count", 0),
                "max_iterations": final_state.get("max_iterations", 2),
                "optimization_directives": final_state.get("optimization_directives", ""),
                "approval_status": final_state.get("approval_status", "pending" if is_interrupted else ""),
                "approval_feedback": final_state.get("approval_feedback", ""),
                "is_approved": final_state.get("is_approved", False),
                "final_response": final_state.get("final_response", ""),
            }
        }
        save_session(thread_id, request.user_input, is_interrupted, next_nodes[0] if next_nodes else None, res_payload["final_state"])
        return res_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@server.post("/api/approve")
def approve_workflow(request: ApprovalRequest):
    if not request.thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required.")
    
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        # Update thread state with human approval decision
        approval_status = "approved" if request.approved else "rejected"
        feedback = request.feedback or ("Approved by user." if request.approved else "Rejected by user.")
        
        graph_app.update_state(
            config,
            {
                "is_approved": request.approved,
                "approval_status": approval_status,
                "approval_feedback": feedback,
            }
        )
        
        trajectory: List[Dict[str, Any]] = []
        
        # Resume graph execution from interrupt checkpoint
        for event in graph_app.stream(None, config=config):
            if isinstance(event, dict):
                items = event.items()
            elif isinstance(event, tuple) and len(event) == 2 and isinstance(event[0], str):
                items = [(event[0], event[1])]
            else:
                items = []

            for node_name, node_state in items:
                if isinstance(node_state, dict):
                    trajectory.append({
                        "node": node_name,
                        "state_update": {
                            k: v for k, v in node_state.items() 
                            if k != "messages"
                        }
                    })
        
        snapshot = graph_app.get_state(config)
        final_state = snapshot.values
        next_nodes = list(snapshot.next) if snapshot.next else []
        
        res_payload = {
            "success": True,
            "thread_id": request.thread_id,
            "is_interrupted": bool(next_nodes),
            "next_node": next_nodes[0] if next_nodes else None,
            "trajectory": trajectory,
            "final_state": {
                "user_input": final_state.get("user_input", ""),
                "agent_response": final_state.get("agent_response", ""),
                "evaluation_score": final_state.get("evaluation_score", 0.0),
                "evaluation_feedback": final_state.get("evaluation_feedback", ""),
                "is_good_enough": final_state.get("is_good_enough", False),
                "approval_status": final_state.get("approval_status", ""),
                "approval_feedback": final_state.get("approval_feedback", ""),
                "is_approved": final_state.get("is_approved", False),
                "final_response": final_state.get("final_response", ""),
            }
        }
        save_session(request.thread_id, final_state.get("user_input", ""), bool(next_nodes), next_nodes[0] if next_nodes else None, res_payload["final_state"])
        return res_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@server.get("/api/stream")
def stream_workflow(user_input: str, thread_id: Optional[str] = "session-demo-1"):
    if not user_input or not user_input.strip():
        raise HTTPException(status_code=400, detail="User input cannot be empty.")
    
    tid = thread_id or "session-demo-1"
    config = {"configurable": {"thread_id": tid}}

    def event_generator():
        try:
            for event in graph_app.stream({"user_input": user_input}, config=config):
                if isinstance(event, dict):
                    items = event.items()
                elif isinstance(event, tuple) and len(event) == 2 and isinstance(event[0], str):
                    items = [(event[0], event[1])]
                else:
                    items = []

                for node_name, node_state in items:
                    if isinstance(node_state, dict):
                        payload = json.dumps({
                            "type": "step",
                            "node": node_name,
                            "state_update": {k: v for k, v in node_state.items() if k != "messages"}
                        })
                        yield f"data: {payload}\n\n"

            snapshot = graph_app.get_state(config)
            final_state = snapshot.values
            next_nodes = list(snapshot.next) if snapshot.next else []
            is_interrupted = bool(next_nodes) and "approval_node" in next_nodes

            complete_payload = json.dumps({
                "type": "complete",
                "thread_id": tid,
                "is_interrupted": is_interrupted,
                "next_node": next_nodes[0] if next_nodes else None,
                "final_state": {
                    "user_input": final_state.get("user_input", ""),
                    "agent_response": final_state.get("agent_response", ""),
                    "evaluation_score": final_state.get("evaluation_score", 0.0),
                    "evaluation_feedback": final_state.get("evaluation_feedback", ""),
                    "is_good_enough": final_state.get("is_good_enough", False),
                    "iteration_count": final_state.get("iteration_count", 0),
                    "max_iterations": final_state.get("max_iterations", 2),
                    "approval_status": final_state.get("approval_status", "pending" if is_interrupted else ""),
                    "approval_feedback": final_state.get("approval_feedback", ""),
                    "is_approved": final_state.get("is_approved", False),
                    "final_response": final_state.get("final_response", ""),
                }
            })
            save_session(tid, user_input, is_interrupted, next_nodes[0] if next_nodes else None, final_state)
            yield f"data: {complete_payload}\n\n"
        except Exception as err:
            err_payload = json.dumps({"type": "error", "error": str(err)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@server.get("/api/state/{thread_id}")
def get_thread_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = graph_app.get_state(config)
    if not state_snapshot or not state_snapshot.values:
        return {"thread_id": thread_id, "exists": False, "state": {}}
    
    values = state_snapshot.values
    next_nodes = list(state_snapshot.next) if state_snapshot.next else []
    return {
        "thread_id": thread_id,
        "exists": True,
        "is_interrupted": bool(next_nodes),
        "next_node": next_nodes[0] if next_nodes else None,
        "state": {
            "user_input": values.get("user_input", ""),
            "evaluation_score": values.get("evaluation_score", 0.0),
            "iteration_count": values.get("iteration_count", 0),
            "approval_status": values.get("approval_status", ""),
            "is_approved": values.get("is_approved", False),
            "final_response": values.get("final_response", ""),
        }
    }


# Serve static web frontend files
os.makedirs("static", exist_ok=True)
server.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    print("Starting Multi-Agent Workflow FastAPI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("server:server", host="127.0.0.1", port=8000, reload=True)
