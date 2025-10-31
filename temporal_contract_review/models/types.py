from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Classification:
    contract_type: str
    complex: bool
    confidence: float


@dataclass
class LegalTerms:
    terms: dict[str, Any]
    entity_names: list[str]
    key_clauses: list[str]


@dataclass
class ValidationResult:
    passed: bool
    issues: list[str]
    confidence: float


@dataclass
class RiskAssessment:
    score: float
    risk_level: str  # "low", "med", "high"
    flags: list[str]


@dataclass
class ReviewResult:
    contract_id: str
    status: str
    classification: Classification
    risk_assessment: RiskAssessment
    total_processing_time: float
