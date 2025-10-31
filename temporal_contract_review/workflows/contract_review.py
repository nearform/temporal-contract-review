from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from temporal_contract_review.models.types import (
    Classification,
    LegalTerms,
    ValidationResult,
    RiskAssessment,
    ReviewResult,
)

from temporal_contract_review.activities.contract_activities import (
    classify_contract,
    extract_legal_terms,
    validate_extraction_quality,
    assess_risk,
    update_crm,
)


@workflow.defn
class ContractReviewWorkflow:
    def __init__(self):
        self.legal_approved = False  # Signal state for HITL
        pass

    @workflow.run
    async def run(self, contract_id: str) -> ReviewResult:
        start_time = workflow.now()

        # DAPER stage: Detect & Classify
        # Integration Debt Solution: Task queue routing based on workflow state
        # Docs: https://docs.temporal.io/workers#task-queues
        classification = await workflow.execute_activity(
            classify_contract,
            contract_id,
            task_queue="cpu-workers",  # Cheap model for classification
            start_to_close_timeout=timedelta(minutes=2),
        )

        # DAPER stage: Analyze
        # Integration debt: Route based on complexity (workflow state)
        # Reliability debt: Retry policy preserves completed work
        # Docs: https://docs.temporal.io/retry-policies
        task_queue = "gpu-workers" if classification.complex else "cpu-workers"
        terms = await workflow.execute_activity(
            extract_legal_terms,
            contract_id,
            task_queue=task_queue,
            retry_policy=RetryPolicy(
                maximum_attempts=3, initial_interval=timedelta(seconds=30)
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Evals: Validate extraction quality before proceeding
        validation = await workflow.execute_activity(
            validate_extraction_quality,
            terms,
            task_queue="cpu-workers",
            start_to_close_timeout=timedelta(minutes=1),
        )

        # AI Safety Guardrail: Failed validation escalates to human review
        # This prevents low-quality AI output from flowing downstream
        if not validation.passed:
            await workflow.wait_condition(lambda: self.legal_approved)

        # DAPER Stage: Plan
        # Visibility debt: Complete workflow history provides provenance
        # All decisions, costs, timings, captured automatically for audit trail
        risk_assessment = await workflow.execute_activity(
            assess_risk,
            terms,
            task_queue="cpu-workers",
            start_to_close_timeout=timedelta(minutes=2),
        )

        # DAPER Stage: Execute
        # Process Coordination Debt: HITL for AI safety guardrails
        # Doc: https://docs.temporal.io/workflows#signals
        if risk_assessment.score > 0.8:
            # High risk contracts require human approval before proceeding
            await workflow.wait_condition(lambda: self.legal_approved)

        # Update CRM with results
        await workflow.execute_activity(
            update_crm,
            args=[contract_id, risk_assessment],
            task_queue="cpu-workers",
            start_to_close_timeout=timedelta(minutes=1),
        )

        # Complete workflow history enables replay based debugging
        # and provides complete provenance trail for regulatory compliance
        end_time = workflow.now()
        total_time = (end_time - start_time).total_seconds()

        return ReviewResult(
            contract_id=contract_id,
            status="approved",
            classification=classification,
            risk_assessment=risk_assessment,
            total_processing_time=total_time,
        )

    @workflow.signal
    async def approve(self):
        """Signal from legal team approving high-risk contract"""
        self.legal_approved = True
