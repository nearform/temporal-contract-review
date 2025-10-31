"""
Tool to send approval signal to a paused high-risk contract workflow.

Usage:
    uv run python -m temporal_contract_review.tools.approve_workflow <workflow-id>

Example:
    uv run python -m temporal_contract_review.tools.approve_workflow contract-review-contract-abc123
"""

import asyncio
import sys
from temporalio.client import Client


async def approve_workflow(workflow_id: str):
    """Send approval signal to resume a paused workflow."""
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)

    print(f"Sending approval signal to workflow: {workflow_id}")
    await handle.signal("approve")
    print(f"✓ Approval signal sent successfully!")
    print(f"Check workflow status at: http://localhost:8233/namespaces/default/workflows/{workflow_id}")


def main():
    """Main entry point for the approval tool."""
    if len(sys.argv) != 2:
        print("Error: Missing workflow ID argument")
        print()
        print("Usage: uv run python -m temporal_contract_review.tools.approve_workflow <workflow-id>")
        print()
        print("Example:")
        print("  uv run python -m temporal_contract_review.tools.approve_workflow contract-review-contract-abc123")
        sys.exit(1)

    workflow_id = sys.argv[1]
    asyncio.run(approve_workflow(workflow_id))


if __name__ == "__main__":
    main()
