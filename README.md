# Persistent Multi-Agent Workflow

An enterprise-grade, stateful, parallel multi-agent workflow architecture built using **LangGraph**, **LangChain**, and **FastAPI**. 

This system demonstrates advanced multi-agent patterns including parallel **Fan-Out / Fan-In** execution across hierarchical subgraphs, iterative **Evaluator-Optimizer self-correction loops**, **Human-in-the-Loop (HITL) execution interrupts**, persistent checkpointing, real-time Server-Sent Events (SSE) streaming, and an interactive modern web dashboard.

---

## 📐 Architecture Diagram

The workflow processes user queries through a structured graph of autonomous agents and specialized subgraphs:

```mermaid
graph TD
    %% Global Nodes
    START([🚀 START: User Input]) --> SUPERVISOR[👑 Supervisor Node]

    %% Fan-Out Parallel Subgraphs
    subgraph Parallel Subgraphs Execution (Fan-Out)
        direction TB
        
        subgraph Research Subgraph
            R1[1. Research] --> R2[2. Analyze] --> R3[3. Summarize]
        end

        subgraph Planner Subgraph
            P1[1. Understand] --> P2[2. Break down] --> P3[3. Create plan]
        end

        subgraph Coder Subgraph
            C1[1. Generate] --> C2[2. Review] --> C3[3. Improve]
        end
    end

    SUPERVISOR --> R1
    SUPERVISOR --> P1
    SUPERVISOR --> C1

    %% Fan-In Aggregation
    R3 --> FANIN[⚡ Fan-In Aggregator Node]
    P3 --> FANIN
    C3 --> FANIN

    %% Evaluator-Optimizer Loop
    FANIN --> EVAL[🔍 Evaluator Node]
    
    EVAL -- "Score < 80 & Iteration < Max (is_good_enough=False)" --> OPT[💡 Optimizer Node]
    OPT -- "Refinement Directives" --> SUPERVISOR

    %% Human-in-the-Loop Interrupt & Approval
    EVAL -- "Score ≥ 80 or Max Iterations (is_good_enough=True)" --> APPROVAL[⏸️ Approval Node (HITL Interrupt)]

    APPROVAL -- "Human Action: APPROVE" --> EXEC[⚙️ Execute Node]
    APPROVAL -- "Human Action: REJECT" --> END_REJECT([❌ END: Rejected])
    
    EXEC --> END_SUCCESS([✅ END: Task Executed])

    %% Styling
    classDef supervisorStyle fill:#4f46e5,stroke:#312e81,color:#ffffff,stroke-width:2px;
    classDef subgraphStyle fill:#1e293b,stroke:#475569,color:#f8fafc;
    classDef aggStyle fill:#0ea5e9,stroke:#0369a1,color:#ffffff,stroke-width:2px;
    classDef evalStyle fill:#f59e0b,stroke:#b45309,color:#ffffff,stroke-width:2px;
    classDef hitlStyle fill:#ec4899,stroke:#be185d,color:#ffffff,stroke-width:2px;
    classDef execStyle fill:#10b981,stroke:#047857,color:#ffffff,stroke-width:2px;

    class SUPERVISOR supervisorStyle;
    class FANIN aggStyle;
    class EVAL,OPT evalStyle;
    class APPROVAL hitlStyle;
    class EXEC execStyle;
```

---

## 🧠 M1–M14 Concepts Learned

This repository systematically implements 14 core foundational concepts of stateful multi-agent systems and LangGraph architecture:

| Module / Concept | Title | Description & Implementation Details | Key Files / References |
| :--- | :--- | :--- | :--- |
| **M1** | **State Management & Custom Reducers** | Built a centralized `AgentState` schema using `TypedDict` and custom channel reducers (`keep_first`, `pick_last`, `add_messages`) to resolve state conflicts during concurrent node execution. | [state.py](file:///d:/Persistent%20Multi-Agent%20Workflow/state.py) |
| **M2** | **Graph Nodes & Edges** | Constructed graph topologies using `StateGraph`, mapping execution logic into isolated node functions and explicit edge transitions from `START` to `END`. | [graph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/graph.py) |
| **M3** | **Sequential Workflows & Chaining** | Orchestrated step-by-step pipeline execution where outputs from upstream nodes are deterministically passed as context to downstream nodes. | [subgraphs/research_subgraph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/subgraphs/research_subgraph.py) |
| **M4** | **Conditional Routing** | Implemented dynamic branch functions (`route_evaluator_decision`, `route_approval_decision`) that direct control flow based on runtime evaluation scores and approval states. | [graph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/graph.py#L13-L33) |
| **M5** | **Supervisor Architecture** | Designed an orchestrator `supervisor_node` that analyzes incoming tasks and dispatches goals to worker agents and specialized sub-agent subgraphs. | [agents/supervisor.py](file:///d:/Persistent%20Multi-Agent%20Workflow/agents/supervisor.py) |
| **M6** | **Parallel Fan-Out / Fan-In Execution** | Achieved concurrent multi-agent execution by dispatching tasks to multiple subgraphs in parallel (**Fan-Out**) and aggregating partial outputs into a unified synthesis (**Fan-In**). | [graph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/graph.py#L66-L74), [agents/fan_in.py](file:///d:/Persistent%20Multi-Agent%20Workflow/agents/fan_in.py) |
| **M7** | **Hierarchical Subgraphs** | Encapsulated domain-specific logic into nested subgraphs (`Research`, `Planner`, `Coder`), each maintaining its own compiled internal 3-stage lifecycle pipeline. | [subgraphs/](file:///d:/Persistent%20Multi-Agent%20Workflow/subgraphs) |
| **M8** | **Evaluator-Optimizer Loops** | Integrated a self-correction feedback loop where an `Evaluator Node` scores task quality and an `Optimizer Node` formulates actionable refinement directives for subsequent execution passes. | [agents/evaluator.py](file:///d:/Persistent%20Multi-Agent%20Workflow/agents/evaluator.py), [agents/optimizer.py](file:///d:/Persistent%20Multi-Agent%20Workflow/agents/optimizer.py) |
| **M9** | **Human-in-the-Loop (HITL) Interrupts** | Applied `interrupt_before=["approval_node"]` to halt graph execution automatically prior to sensitive operations, requiring human authorization. | [graph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/graph.py#L110), [agents/approval.py](file:///d:/Persistent%20Multi-Agent%20Workflow/agents/approval.py) |
| **M10** | **State Checkpointing & Persistence** | Integrated `MemorySaver` checkpointer to serialize state snapshots indexed by `thread_id`, preserving full execution history across requests. | [graph.py](file:///d:/Persistent%20Multi-Agent%20Workflow/graph.py#L106-L111) |
| **M11** | **Workflow Resumption & Modification** | Enabled graph execution resumption from persisted checkpoints using `app.update_state()` to inject human feedback before triggering `app.stream(None, config)`. | [server.py](file:///d:/Persistent%20Multi-Agent%20Workflow/server.py#L170-L182), [main.py](file:///d:/Persistent%20Multi-Agent%20Workflow/main.py#L27-L37) |
| **M12** | **FastAPI Backend Integration** | Built a production REST API serving session management (`/api/threads`), state inspection (`/api/state`), workflow invocation (`/api/run`), and approval handling (`/api/approve`). | [server.py](file:///d:/Persistent%20Multi-Agent%20Workflow/server.py) |
| **M13** | **Real-Time SSE Streaming** | Implemented a Server-Sent Events endpoint (`/api/stream`) streaming real-time node execution steps and state updates directly to clients. | [server.py](file:///d:/Persistent%20Multi-Agent%20Workflow/server.py#L228-L285) |
| **M14** | **Interactive Web Interface** | Created a glassmorphism frontend dashboard (`static/index.html`) featuring visual graph progress tracking, live SSE logs, sub-graph output tabs, and an interactive HITL modal. | [static/index.html](file:///d:/Persistent%20Multi-Agent%20Workflow/static/index.html), [static/app.js](file:///d:/Persistent%20Multi-Agent%20Workflow/static/app.js) |

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- `pip` package manager

### 1. Installation
Clone the repository and install the dependencies:
```bash
pip install fastapi uvicorn langgraph langchain-core pydantic
```

### 2. Running the FastAPI Server & Web Dashboard
Launch the FastAPI backend server:
```bash
python server.py
```
* The backend API server will start at: `http://127.0.0.1:8000`
* Open your browser and navigate to `http://127.0.0.1:8000` to launch the **Interactive Web Dashboard**.

### 3. Running the CLI Demonstration
To test the workflow execution, persistent checkpointing, and Human-in-the-Loop (HITL) approve/reject paths directly in your terminal:
```bash
python main.py
```

---

## 🌐 Environment Variables

This workflow can run locally without external API dependencies using default simulated nodes, or can be configured with LLM providers:

| Variable | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `PORT` | Port number for the FastAPI backend server. | `8000` | Optional |
| `HOST` | Binding host address for Uvicorn. | `127.0.0.1` | Optional |
| `OPENAI_API_KEY` | OpenAI API Key (if extending nodes to use `ChatOpenAI`). | `None` | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API Key (if extending nodes to use `ChatAnthropic`). | `None` | Optional |

---

## 📡 API Endpoints

The FastAPI server exposes the following REST and SSE streaming endpoints:

| Endpoint | Method | Description | Request Body / Query Params |
| :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | Health check endpoint returning backend status. | None |
| `/api/threads` | `GET` | Lists all active and historical workflow sessions with metadata. | None |
| `/api/run` | `POST` | Triggers a workflow run. Executes until completed or interrupted at HITL node. | `{ "user_input": "...", "thread_id": "session-1" }` |
| `/api/stream` | `GET` | SSE stream endpoint delivering real-time graph step updates and final complete event. | `?user_input=...&thread_id=session-1` |
| `/api/approve` | `POST` | Resumes an interrupted workflow session with human review decision (`approved: true/false`). | `{ "thread_id": "session-1", "approved": true, "feedback": "Looks good!" }` |
| `/api/state/{thread_id}` | `GET` | Inspects current state snapshot and next pending node for a thread. | Path Parameter: `thread_id` |

---

## 🔄 Example Workflow

Here is the step-by-step lifecycle of an execution request:

1. **Task Submission**: User submits prompt: *"Design and implement a RAG-powered chatbot in Python"*.
2. **Supervisor Fan-Out**: The `Supervisor Node` dispatches the task concurrently to three subgraphs:
   - **Research Subgraph**: `Research` ➔ `Analyze` ➔ `Summarize`
   - **Planner Subgraph**: `Understand` ➔ `Break down` ➔ `Create plan`
   - **Coder Subgraph**: `Generate` ➔ `Review` ➔ `Improve`
3. **Fan-In Aggregation**: The `Fan-In Aggregator Node` waits for all three subgraphs to finish and synthesizes their partial outputs.
4. **Evaluator Check**: The `Evaluator Node` checks synthesis quality:
   - **Pass 1**: Quality score is 70.0 (`is_good_enough = False`). Control routes to `Optimizer Node`.
   - **Optimizer Directives**: `Optimizer Node` adds security and containerization requirements, routing back to `Supervisor`.
   - **Pass 2**: Subgraphs re-execute with optimization directives. Score reaches 95.0 (`is_good_enough = True`). Control routes to `Approval Node`.
5. **Human Interrupt (HITL)**: Workflow hits `interrupt_before=["approval_node"]`. Execution pauses and saves checkpoint under `thread_id`.
6. **Human Decision**:
   - **If Approved**: `update_state(is_approved=True)` ➔ Resumes to `Execute Node` ➔ Task Deployed ➔ `END`.
   - **If Rejected**: `update_state(is_approved=False)` ➔ Resumes to `END` without execution.

---

## ⏸️ Resume / HITL Explanation

Human-in-the-Loop (HITL) execution and state resumption form the core resilience layer of this persistent multi-agent framework:

### How Interrupts & Persistence Work:
1. **Compilation with Checkpointer**:
   ```python
   checkpointer = MemorySaver()
   app = workflow.compile(
       checkpointer=checkpointer,
       interrupt_before=["approval_node"]
   )
   ```
2. **Execution Halt**: When execution reaches `approval_node`, LangGraph writes the current `AgentState` snapshot into `MemorySaver` under `thread_id` and suspends execution.
3. **State Inspection**: The state snapshot can be inspected anytime via:
   ```python
   snapshot = app.get_state({"configurable": {"thread_id": thread_id}})
   print(snapshot.next)   # Output: ('approval_node',)
   print(snapshot.values) # Output: Dict of full AgentState
   ```
4. **State Modification & Resumption**: When a human reviewer approves or rejects via Web UI or CLI:
   ```python
   # Inject decision into state snapshot
   app.update_state(
       config={"configurable": {"thread_id": thread_id}},
       values={"is_approved": True, "approval_status": "approved", "approval_feedback": "Approved for production."}
   )

   # Resume execution passing None as input to continue from checkpoint
   for event in app.stream(None, config=config):
       print(event)
   ```
This architecture guarantees zero lost work and complete auditability for complex human-reviewed AI pipelines.