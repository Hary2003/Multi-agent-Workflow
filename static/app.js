let activeThreadId = 'session-ui-101';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('workflow-form');
    const promptInput = document.getElementById('prompt-input');
    const threadInput = document.getElementById('thread-input');
    const runBtn = document.getElementById('run-btn');
    const btnSpinner = document.getElementById('btn-spinner');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = promptInput.value.trim();
        const threadId = threadInput.value.trim() || 'session-ui-101';
        activeThreadId = threadId;

        if (!userInput) return;

        // UI Reset & Start State
        runBtn.disabled = true;
        btnSpinner.classList.remove('hidden');
        resetNodeHighlights();
        hideApprovalModal();

        logToTerminal(`[Client] Initiating task execution on thread '${threadId}'...`, 'log-info');
        logToTerminal(`[Prompt] "${userInput}"`, 'log-entry');

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
            
            // Replay trajectory nodes with visual step animations
            await replayTrajectory(data.trajectory);

            // Display current results
            displayResults(data.final_state, data.is_interrupted);

            if (data.is_interrupted) {
                logToTerminal(`[Approval Node] ⏸ INTERRUPT: Graph execution paused at Approval Node. Awaiting human decision.`, 'log-warn');
                highlightNode('approval_node');
                showApprovalModal(data.final_state);
            } else {
                logToTerminal(`[System] Multi-agent execution completed successfully. Thread '${threadId}' state saved.`, 'log-success');
                highlightNode('END');
            }
        } catch (err) {
            logToTerminal(`[Error] ${err.message}`, 'log-warn');
        } finally {
            runBtn.disabled = false;
            btnSpinner.classList.add('hidden');
        }
    });
});

// Submit Human Approval (Approve / Reject)
async function submitApproval(approved) {
    const feedbackInput = document.getElementById('approval-feedback-input');
    const feedback = feedbackInput.value.trim();
    const threadInput = document.getElementById('thread-input');
    const threadId = threadInput.value.trim() || activeThreadId || 'session-ui-101';

    hideApprovalModal();
    logToTerminal(`[Client] Submitting human approval decision: ${approved ? 'APPROVED' : 'REJECTED'} (Feedback: "${feedback}")`, 'log-info');

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
            logToTerminal(`[System] Task APPROVED by user. Graph reached END node.`, 'log-success');
            highlightNode('END');
        } else {
            logToTerminal(`[System] Task REJECTED by user. Re-routed to Optimizer for loop refinement.`, 'log-warn');
            highlightNode('optimizer');
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
