import asyncio
import random

from temporalio import activity

from temporal_contract_review.models.types import (
    Classification,
    LegalTerms,
    ValidationResult,
    RiskAssessment,
)


@activity.defn
async def classify_contract(contract_id: str) -> Classification:
    """Stub: Classify contract type and complexity"""
    # Simulate AI processing time (cheap/fast model)
    await asyncio.sleep(1.0)

    # Return realistic stub data
    return Classification(
        contract_type=random.choice(["NDA", "MSA", "SOW", "Vendor Agreement"]),
        complex=random.choice([True, False]),
        confidence=random.uniform(0.85, 0.99),
    )


@activity.defn
async def extract_legal_terms(contract_id: str) -> LegalTerms:
    """Stub: Extract legal terms"""
    # Simulate expensive AI call
    await asyncio.sleep(2.0)

    return LegalTerms(
        terms={"payment_terms": "Net 30", "jurisdiction": "Delaware"},
        entity_names=["Acme Corp", "Beta LLC"],
        key_clauses=["Indemnification", "Confidentiality", "Termination"],
    )


@activity.defn
async def validate_extraction_quality(terms: LegalTerms) -> ValidationResult:
    """Stub: Validate AI extraction quality (Evals)"""
    await asyncio.sleep(0.5)

    # Simulate validation pass/fail (90% pass rate)
    passed = random.random() > 0.1

    return ValidationResult(
        passed=passed,
        issues=[] if passed else ["Missing entity names", "Low confidence"],
        confidence=random.uniform(0.8, 0.95),
    )


@activity.defn
async def assess_risk(terms: LegalTerms) -> RiskAssessment:
    """Stub: Assess contract risk"""
    await asyncio.sleep(1.5)

    score = random.uniform(0.0, 1.0)
    risk_level = "high" if score > 0.8 else "medium" if score > 0.5 else "low"

    return RiskAssessment(
        score=score,
        risk_level=risk_level,
        flags=["Unusual indemnification clause"] if score > 0.8 else [],
    )


@activity.defn
async def update_crm(contract_id: str, risk_assessment: RiskAssessment) -> None:
    """Stub: Update CRM system"""
    await asyncio.sleep(0.8)
    activity.logger.info(
        f"CRM updated for contract {contract_id}:{risk_assessment.risk_level} risk"
    )
