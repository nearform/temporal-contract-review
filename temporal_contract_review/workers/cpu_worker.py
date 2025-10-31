import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from temporal_contract_review.workflows.contract_review import ContractReviewWorkflow
from temporal_contract_review.activities.contract_activities import (
    classify_contract,
    extract_legal_terms,
    validate_extraction_quality,
    assess_risk,
    update_crm,
)


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="cpu-workers",
        workflows=[ContractReviewWorkflow],
        activities=[
            classify_contract,
            extract_legal_terms,
            validate_extraction_quality,
            assess_risk,
            update_crm,
        ],
    )
    print("CPU Worker started, polling 'cpu-workers' task queue")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
