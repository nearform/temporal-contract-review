import asyncio
import uuid

from temporalio.client import Client

from temporal_contract_review.workflows.contract_review import ContractReviewWorkflow
from temporal_contract_review.models.types import ReviewResult


async def main():
    """Start contract review workflow"""
    client = await Client.connect("localhost:7233")

    # Generate a unique contract ID
    contract_id = f"contract-{uuid.uuid4().hex[:8]}"

    print(f"Starting contract review workflow for: {contract_id}")

    # Start workflow execution
    handle = await client.start_workflow(
        ContractReviewWorkflow.run,
        contract_id,
        id=f"contract-review-{contract_id}",
        task_queue="cpu-workers",
    )

    print(f"Workflow started with ID: {handle.id}")
    print(
        f"Track in UI: http://localhost:8233/namespaces/default/workflows/{handle.id}"
    )

    # Wait for result
    result: ReviewResult = await handle.result()

    print(f"\nWorkflow completed!")
    print(f"Contract ID: {result.contract_id}")
    print(f"Status: {result.status}")
    print(
        f"Classification: {result.classification.contract_type}( {'complex' if result.classification.complex else 'simple'})"
    )
    print(
        f"Risk: {result.risk_assessment.risk_level} (score: {result.risk_assessment.score:.2f})"
    )
    print(f"Processing time: {result.total_processing_time:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
