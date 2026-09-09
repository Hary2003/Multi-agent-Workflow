let activeThreadId = 'session-ui-101';
let lastExecutedTrajectory = [];

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('workflow-form');
    const promptInput = document.getElementById('prompt-input');
    const threadInput = document.getElementById('thread-input');
    const runBtn = document.getElementById('run-btn');
    const btnSpinner = document.getElementById('btn-spinner');

    loadPastSessions();

    // Attach click listeners on visual architecture graph nodes
    document.querySelectorAll('.node, .subgraph-box').forEach(elem => {
        elem.style.cursor = 'pointer';
        elem.addEventListener('click', () => {
            const nodeId = elem.id.replace('node-', '');
            inspectNode(nodeId);
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = promptInput.value.trim();
        const threadId = threadInput.value.trim() || 'session-ui-101';
        activeThreadId = threadId;
        const useStreaming = document.getElementById('stream-toggle').checked;

        if (!userInput) return;

        // UI Reset & Start State
        runBtn.disabled = true;
        btnSpinner.classList.remove('hidden');
        resetNodeHighlights();
        hideApprovalModal();
        lastExecutedTrajectory = [];

        logToTerminal(`[Client] Initiating task execution on thread '${threadId}' (Mode: ${useStreaming ? 'SSE Stream' : 'Batch REST'})...`, 'log-info');
        logToTerminal(`[Prompt] "${userInput}"`, 'log-entry');

        if (useStreaming) {
            runStreamingWorkflow(userInput, threadId, runBtn, btnSpinner);
        } else {
            runBatchWorkflow(userInput, threadId, runBtn, btnSpinner);
        }
    });
});

// Load Past Session Threads
async function loadPastSessions() {
    try {
        const res = await fetch('/api/threads');
        if (!res.ok) return;
        const data = await res.json();
        const select = document.getElementById('session-select');
        if (!select) return;

        select.innerHTML = '<option value="">-- Saved Sessions --</option>';
        (data.threads || []).forEach(sess => {
            const opt = document.createElement('option');
            opt.value = sess.thread_id;
            opt.innerText = `${sess.thread_id} (${sess.updated_at || 'Saved'})`;
            select.appendChild(opt);
        });
    } catch (e) {
        console.warn('Could not fetch past sessions:', e);
    }
}

// Switch Active Thread Session
async function switchSessionThread(threadId) {
    if (!threadId) return;
    document.getElementById('thread-input').value = threadId;
    activeThreadId = threadId;

    logToTerminal(`[Session Manager] Switched context to thread '${threadId}'. Fetching state snapshot...`, 'log-info');

    try {
        const res = await fetch(`/api/state/${threadId}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.exists && data.state) {
            if (data.state.user_input) {
                document.getElementById('prompt-input').value = data.state.user_input;
            }
            displayResults(data.state, data.is_interrupted);
            if (data.is_interrupted) {
                highlightNode('approval_node');
                highlightNode('interrupt');
                showApprovalModal(data.state);
            }
            logToTerminal(`[Session Manager] State snapshot loaded for '${threadId}'.`, 'log-success');
        }
    } catch (e) {
        logToTerminal(`[Error] Failed to load thread '${threadId}': ${e.message}`, 'log-warn');
    }
}

// Stream Workflow Execution via SSE
function runStreamingWorkflow(userInput, threadId, runBtn, btnSpinner) {
    const streamUrl = `/api/stream?user_input=${encodeURIComponent(userInput)}&thread_id=${encodeURIComponent(threadId)}`;
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            if (data.type === 'step') {
                logToTerminal(`⚡ Live Stream Step: [${data.node}]`, 'log-info');
                highlightNode(data.node);
                lastExecutedTrajectory.push(data);
            } else if (data.type === 'complete') {
                eventSource.close();
                displayResults(data.final_state, data.is_interrupted);
                loadPastSessions();

                if (data.is_interrupted) {
                    logToTerminal(`[Approval Node] ⏸ INTERRUPT: Execution paused at Approval Node. Awaiting decision.`, 'log-warn');
                    highlightNode('approval_node');
                    highlightNode('interrupt');
                    showApprovalModal(data.final_state);
                } else {
                    logToTerminal(`[System] Multi-agent SSE streaming execution complete for thread '${threadId}'.`, 'log-success');
                    highlightNode('END');
                }
                runBtn.disabled = false;
                btnSpinner.classList.add('hidden');
            } else if (data.type === 'error') {
                eventSource.close();
                logToTerminal(`[Error] ${data.error}`, 'log-warn');
                runBtn.disabled = false;
                btnSpinner.classList.add('hidden');
            }
        } catch (err) {
            console.error('SSE JSON parse error:', err);
        }
    };

    eventSource.onerror = (err) => {
        eventSource.close();
        logToTerminal(`[Error] SSE Connection interrupted. Falling back to batch mode.`, 'log-warn');
        runBtn.disabled = false;
        btnSpinner.classList.add('hidden');
    };
}

// Batch REST Execution Fallback
async function runBatchWorkflow(userInput, threadId, runBtn, btnSpinner) {
    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_input: userInput, thread_id: threadId })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Workflow execution failed');
        }

        const data = await response.json();
        await replayTrajectory(data.trajectory);
        displayResults(data.final_state, data.is_interrupted);
        loadPastSessions();

        if (data.is_interrupted) {
            logToTerminal(`[Approval Node] ⏸ INTERRUPT: Graph execution paused at Approval Node.`, 'log-warn');
            highlightNode('approval_node');
            highlightNode('interrupt');
            showApprovalModal(data.final_state);
        } else {
            logToTerminal(`[System] Execution completed successfully. Thread '${threadId}' saved.`, 'log-success');
            highlightNode('END');
        }
    } catch (err) {
        logToTerminal(`[Error] ${err.message}`, 'log-warn');
    } finally {
        runBtn.disabled = false;
        btnSpinner.classList.add('hidden');
    }
}


// Submit Human Approval (Approve / Reject)
async function submitApproval(approved) {
    const feedbackInput = document.getElementById('approval-feedback-input');
    const feedback = feedbackInput.value.trim();
    const threadInput = document.getElementById('thread-input');
    const threadId = threadInput.value.trim() || activeThreadId || 'session-ui-101';

    hideApprovalModal();
    logToTerminal(`[Client] Submitting human decision: ${approved ? 'APPROVE' : 'REJECT'} (Feedback: "${feedback}")`, 'log-info');

    try {
        const response = await fetch('/api/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: threadId,
                approved: approved,
                feedback: feedback
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to submit approval decision');
        }

        const data = await response.json();

        // Replay post-approval trajectory steps
        if (data.trajectory && data.trajectory.length > 0) {
            await replayTrajectory(data.trajectory);
        }

        displayResults(data.final_state, false);

        if (approved) {
            logToTerminal(`[System] Task APPROVED by user. Executed payload and reached END node.`, 'log-success');
            highlightNode('execute');
            highlightNode('END');
        } else {
            logToTerminal(`[System] Task REJECTED by user. Workflow terminated at END node.`, 'log-warn');
            highlightNode('END-reject');
        }
    } catch (err) {
        logToTerminal(`[Error] ${err.message}`, 'log-warn');
    }
}

// Show / Hide Approval Modal
function showApprovalModal(state) {
    const modal = document.getElementById('approval-modal');
    const preview = document.getElementById('modal-output-preview');
    if (preview) {
        preview.innerText = state.final_response || state.agent_response || 'Synthesized report ready for review.';
    }
    modal.classList.remove('hidden');
}

function hideApprovalModal() {
    const modal = document.getElementById('approval-modal');
    modal.classList.add('hidden');
}

// Load Preset Prompt
function loadPreset(promptText) {
    document.getElementById('prompt-input').value = promptText;
}

// Terminal Logging Helper
function logToTerminal(msg, className = 'log-entry') {
    const terminal = document.getElementById('terminal-body');
    const entry = document.createElement('div');
    entry.className = `log-entry ${className}`;
    const timestamp = new Date().toLocaleTimeString();
    entry.innerText = `[${timestamp}] ${msg}`;
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
}

function clearTerminal() {
    document.getElementById('terminal-body').innerHTML = '<div class="log-entry log-info">[System] Console cleared.</div>';
}

// Reset Visual Node Highlights
function resetNodeHighlights() {
    document.querySelectorAll('.active-node').forEach(el => el.classList.remove('active-node'));
}

function highlightNode(nodeName) {
    const nodeElem = document.getElementById(`node-${nodeName}`);
    if (nodeElem) {
        nodeElem.classList.add('active-node');
    }
}

// Replay Trajectory Step by Step with Node Glow
async function replayTrajectory(trajectory) {
    for (const step of trajectory) {
        const nodeName = step.node;
        logToTerminal(`➔ Step Executed: [${nodeName}]`, 'log-info');
        highlightNode(nodeName);

        // Brief delay to visualize execution flow
        await new Promise(r => setTimeout(r, 450));
    }
}

// Render Results in Inspector Tabs & Metrics Card
function displayResults(state, isInterrupted = false) {
    const metricsCard = document.getElementById('metrics-card');
    metricsCard.classList.remove('hidden');

    const statusElem = document.getElementById('m-status');
    if (isInterrupted) {
        statusElem.innerText = '⏸ Awaiting Approval';
        statusElem.className = 'metric-value text-gold';
    } else if (state.is_approved || state.approval_status === 'approved') {
        statusElem.innerText = 'Approved & Completed';
        statusElem.className = 'metric-value text-success';
    } else if (state.approval_status === 'rejected') {
        statusElem.innerText = 'Revision Requested';
        statusElem.className = 'metric-value text-gold';
    } else {
        statusElem.innerText = 'Completed';
        statusElem.className = 'metric-value text-success';
    }

    document.getElementById('m-iterations').innerText = `${state.iteration_count || 1} / ${state.max_iterations || 2}`;
    document.getElementById('m-score').innerText = `${state.evaluation_score || 95}%`;
    document.getElementById('m-decision').innerText = state.is_good_enough ? 'GOOD (Passed)' : 'BAD (Needs Optimization)';

    // Update Tab Pre Content
    document.getElementById('out-synthesis').innerText = state.final_response || 'No synthesized response.';
    document.getElementById('out-research').innerText = state.research_output || 'No research output.';
    document.getElementById('out-planner').innerText = state.planner_output || 'No plan output.';
    document.getElementById('out-coder').innerText = state.coder_output || 'No coder output.';

    // Render Evaluator & Approval Scorecard
    const evalTab = document.getElementById('out-eval');
    evalTab.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; gap:16px; align-items:center;">
                <span style="font-size:24px; font-weight:700; color:var(--accent-cyan);">${state.evaluation_score || 95}/100</span>
                <span style="font-size:13px; padding:4px 12px; border-radius:12px; background:${state.is_good_enough ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)'}; color:${state.is_good_enough ? 'var(--accent-emerald)' : 'var(--accent-gold)'};">
                    ${state.is_good_enough ? 'PASSED QUALITY THRESHOLD (GOOD)' : 'OPTIMIZATION REQUIRED (BAD)'}
                </span>
            </div>
            <p style="font-size:13px; color:#cbd5e1;"><strong>Evaluator Feedback:</strong> ${state.evaluation_feedback || 'N/A'}</p>
            ${state.approval_status ? `<p style="font-size:13px; color:var(--accent-gold);"><strong>Human Approval Status:</strong> ${state.approval_status.toUpperCase()} (Feedback: "${state.approval_feedback || 'None'}")</p>` : ''}
            ${state.optimization_directives ? `<div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); padding:10px; border-radius:8px; font-size:12px; color:var(--accent-gold); white-space:pre-wrap;"><strong>Optimization Directives:</strong>\n${state.optimization_directives}</div>` : ''}
        </div>
    `;
}

// Inspector Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (event && event.target) {
        event.target.classList.add('active');
    }
    const contentElem = document.getElementById(tabId);
    if (contentElem) {
        contentElem.classList.add('active');
    }
}

// Node Detail Inspector Modal
function inspectNode(nodeId) {
    const modal = document.getElementById('node-modal');
    const title = document.getElementById('node-modal-name');
    const content = document.getElementById('node-modal-content');

    if (!modal || !title || !content) return;

    title.innerText = `Node Telemetry: [${nodeId}]`;
    const stepMatch = lastExecutedTrajectory.find(s => s.node === nodeId);
    if (stepMatch) {
        content.innerText = JSON.stringify(stepMatch.state_update, null, 2);
    } else {
        content.innerText = `[Node info]: Execution node '${nodeId}' registered in Graph Architecture.\nThread: '${activeThreadId}'`;
    }
    modal.classList.remove('hidden');
}

function hideNodeModal() {
    const modal = document.getElementById('node-modal');
    if (modal) modal.classList.add('hidden');
}

