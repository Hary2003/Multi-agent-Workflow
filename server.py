import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from graph import app as graph_app

server = FastAPI(
    title="Persistent Multi-Agent Workflow API",
    description="FastAPI backend serving the LangGraph parallel multi-agent graph with subgraphs and Evaluator-Optimizer loop.",
    version="1.0.0"
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


@server.get("/api/health")
def health_check():
    return {"status": "online", "message": "Multi-Agent Workflow Engine Operational"}


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
            for node_name, node_state in event.items():
                trajectory.append({
                    "node": node_name,
                    "state_update": {
                        k: v for k, v in node_state.items() 
                        if k != "messages" # Messages format handled separately
                    }
                })
        
        # Get final checkpoint state
        final_state = graph_app.get_state(config).values
        
        return {
            "success": True,
            "thread_id": thread_id,
            "user_input": request.user_input,
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
                "final_response": final_state.get("final_response", ""),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@server.get("/api/state/{thread_id}")
def get_thread_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = graph_app.get_state(config)
    if not state_snapshot or not state_snapshot.values:
        return {"thread_id": thread_id, "exists": False, "state": {}}
    
    values = state_snapshot.values
    return {
        "thread_id": thread_id,
        "exists": True,
        "state": {
            "user_input": values.get("user_input", ""),
            "evaluation_score": values.get("evaluation_score", 0.0),
            "iteration_count": values.get("iteration_count", 0),
            "final_response": values.get("final_response", ""),
        }
    }


# Serve static web frontend files
os.makedirs("static", exist_ok=True)
server.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    print("Starting Multi-Agent Workflow FastAPI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("server:server", host="127.0.0.1", port=8000, reload=True)
