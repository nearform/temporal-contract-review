import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from temporal_contract_review.workflows.contract_review import ContractReviewWorkflow
from temporal_contract_review.activities.contracts_activities import (
    extract_legal_terms,
    validate_extraction_quality,
    assess_risk,
)


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="gpu-workers",
        workflows=[ContractReviewWorkflow],
        activities=[
            extract_legal_terms,
            validate_extraction_quality,
            assess_risk,
        ],
    )
    print("GPU Worker started, polling 'gpu-workers' task queue")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
