from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class KYCStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class CustomerData(BaseModel):
    name: str
    dob: str  # YYYY-MM-DD
    nationality: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class DocumentExtractionResult(BaseModel):
    document_type: str  # passport, national_id, driving_license
    full_name: Optional[str] = None
    dob: Optional[str] = None
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None
    nationality: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class LivenessResult(BaseModel):
    face_match_score: float = Field(ge=0.0, le=1.0)
    is_live: bool
    spoof_detected: bool


class SanctionsResult(BaseModel):
    is_sanctioned: bool
    is_pep: bool  # Politically Exposed Person
    matches: list[dict] = []


class AdverseMediaResult(BaseModel):
    has_adverse_media: bool
    severity: Optional[str] = None  # low, medium, high
    articles: list[dict] = []


class KYCRiskScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    factors: dict = {}


class KYCCase(BaseModel):
    case_id: str
    customer: CustomerData
    status: KYCStatus = KYCStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    document_result: Optional[DocumentExtractionResult] = None
    liveness_result: Optional[LivenessResult] = None
    sanctions_result: Optional[SanctionsResult] = None
    adverse_media_result: Optional[AdverseMediaResult] = None
    risk_score: Optional[KYCRiskScore] = None
    decision_reason: Optional[str] = None
    analyst_notes: Optional[str] = None
