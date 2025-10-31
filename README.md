# Temporal Contract Review Workflow - Validation Repository

## Purpose

This repository validates the contract review workflow code from the article "Architectural Debt: The AI Tax You Are Already Paying." It proves that Temporal's orchestration primitives work as described without claiming to solve legal AI.

**What This Demonstrates:**
- Integration Debt remediation: Dynamic task queue routing
- Reliability Debt remediation: Retry policies preserve expensive work
- Visibility Debt remediation: Complete workflow history and provenance
- Process Coordination Debt remediation: Human in the loop (HITL) patterns
- AI Evals: Validation activities ensure output quality
- Debugging: Replay based debugging via workflow history

**What This Is NOT:**
- NOT a production ready legal AI system
- NOT real LLM integrations
- NOT solving legal contract analysis
- Activities are STUBS returning dummy data

## Prerequisites

- Python 3.12+
- uv (Python package manager)
- Temporal CLI (recommended) OR Docker + Docker Compose (alternative)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/[org]/temporal-contract-review.git
cd temporal-contract-review
```

2. Install Python dependencies with uv:
```bash
uv sync
```

3. Start Temporal server (choose one):

**Option A: Temporal CLI Dev Server (Recommended)**
```bash
temporal server start-dev
```

**Option B: Docker Compose**
```bash
docker-compose up -d
```

## Running the Workflow

You'll need 3 terminal windows:

**Terminal 1 - CPU Worker:**
```bash
uv run python -m temporal_contract_review.workers.cpu_worker
```

**Terminal 2 - GPU Worker (optional):**
```bash
uv run python -m temporal_contract_review.workers.gpu_worker
```

**Terminal 3 - Start Workflow:**
```bash
uv run python -m temporal_contract_review.starter.start_workflow
```

## View in Temporal Web UI

Open http://localhost:8233 to see:
- Complete workflow execution history
- Activity routing to different task queues
- Retry behavior when activities fail
- HITL pause for high risk contracts
- Full audit trail and provenance

## What Gets Demonstrated

### Integration Debt - Task Queue Routing
- Classification activity runs on cpu-workers (cheap model)
- Complex contracts route extraction to gpu-workers (expensive model)
- Simple contracts route to cpu-workers
- Workflow decides routing based on state (complexity)

### Reliability Debt - Retry Policies
- Extraction activity has retry policy (max 3 attempts, 30s backoff)
- If extraction fails on attempt 1, Temporal retries without re-running classification
- Completed work (classification) is preserved in event history
- No external state storage needed

### Visibility Debt - Workflow History
- Complete execution history captured automatically
- Every activity, decision, timing, state transition recorded
- Replay workflow to see exactly what happened
- Audit trail for "Why did this contract route to manual review?"

### Process Coordination Debt - HITL Signals
- High risk contracts (score > 0.8) pause awaiting approval
- Failed AI validation also triggers human review (AI safety guardrail)
- Workflow can pause indefinitely (days) without losing state
- Legal team sends approve signal to resume
- Complete workflow context preserved across pause

### AI Evals
- validate_extraction_quality activity checks AI output quality
- Failed validation escalates to human review (second HITL scenario)
- Prevents bad data from flowing downstream

## Testing HITL Flow

The workflow will pause awaiting approval in two scenarios:
1. **High risk contract** (score > 0.8, random ~10% chance)
2. **Failed validation** (quality check fails, random ~10% chance)

You'll see in the Temporal Web UI that the workflow is "Running" but waiting at a condition.

### Option 1: Using Temporal CLI (Recommended - Easiest)

```bash
# Send approval signal using Temporal CLI
temporal workflow signal \
  --workflow-id contract-review-contract-abc123 \
  --name approve
```

Replace contract-review-contract-abc123 with the actual workflow ID from the starter output.

### Option 2: Using Python Script (Programmatic Approach)

Run the included approval tool:

```bash
uv run python -m temporal_contract_review.tools.approve_workflow contract-review-contract-abc123
```

Or create a custom script approve_workflow.py:
```python
import asyncio
import sys
from temporalio.client import Client

async def approve_workflow(workflow_id: str):
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("approve")
    print(f"Sent approval signal to {workflow_id}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python approve_workflow.py <workflow-id>")
        sys.exit(1)

    asyncio.run(approve_workflow(sys.argv[1]))
```

Then run:
```bash
uv run python approve_workflow.py contract-review-contract-abc123
```

After sending the signal, the workflow will resume and complete successfully.

## Architecture

- **Workflows**: Contain orchestration logic (routing, retry, HITL)
- **Activities**: Contain business logic (stub AI calls)
- **Workers**: Poll task queues and execute activities
- **Task Queues**: Route work to specific worker pools (CPU vs GPU)

## Project Structure

```
temporal-contract-review/
├── README.md
├── pyproject.toml
├── .python-version
└── temporal_contract_review/
    ├── models/
    │   └── types.py                  # Result dataclasses
    ├── activities/
    │   └── contract_activities.py    # 5 stub activities
    ├── workflows/
    │   └── contract_review.py        # ContractReviewWorkflow
    ├── workers/
    │   ├── cpu_worker.py             # CPU worker (cheap models)
    │   └── gpu_worker.py             # GPU worker (expensive models)
    ├── starter/
    │   └── start_workflow.py         # Workflow starter CLI
    └── tools/
        └── approve_workflow.py       # HITL approval helper
```

## Relationship to Article

This repo validates the orchestration patterns shown in the article. The article code (35-45 lines) focuses on orchestration patterns with inline doc links. This repo proves those patterns work with a complete runnable implementation.

## Resources

**Temporal Documentation:**
- Task Queues: https://docs.temporal.io/workers#task-queues
- Retry Policies: https://docs.temporal.io/retry-policies
- Workflow History: https://docs.temporal.io/visibility
- Signals: https://docs.temporal.io/workflows#signals
- Python SDK: https://python.temporal.io/temporalio.workflow.html

**Inspiration:**
- Multi-agent order repair sample: https://github.com/joshmsmith/temporal-multi-agent-order-repair
- Shows DAPER pattern in production context

## License

MIT
