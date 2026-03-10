"""Risk scoring engine — combines all KYC signals into a composite score."""
from models.kyc import KYCCase, KYCRiskScore, RiskLevel


def calculate_risk_score(case: KYCCase) -> KYCRiskScore:
    score = 0.0
    factors = {}

    # Document quality (max 20 pts)
    if case.document_result:
        doc_score = case.document_result.confidence * 20
        score += doc_score
        factors["document_confidence"] = f"{case.document_result.confidence:.0%}"
    
    # Liveness (max 30 pts)
    if case.liveness_result:
        if case.liveness_result.spoof_detected:
            factors["liveness"] = "spoof_detected"
        elif not case.liveness_result.is_live:
            factors["liveness"] = "failed"
        else:
            face_score = case.liveness_result.face_match_score * 30
            score += face_score
            factors["face_match"] = f"{case.liveness_result.face_match_score:.0%}"

    # Sanctions (binary, heavy penalty)
    if case.sanctions_result:
        if case.sanctions_result.is_sanctioned:
            score = 0  # hard fail
            factors["sanctions"] = "HIT"
        elif case.sanctions_result.is_pep:
            score -= 20
            factors["pep"] = True
        else:
            score += 30
            factors["sanctions"] = "clear"

    # Adverse media (max 20 pts)
    if case.adverse_media_result:
        if not case.adverse_media_result.has_adverse_media:
            score += 20
            factors["adverse_media"] = "clear"
        elif case.adverse_media_result.severity == "low":
            score += 10
            factors["adverse_media"] = "low_risk"
        else:
            factors["adverse_media"] = f"found_{case.adverse_media_result.severity}"

    # Clamp 0-100
    score = max(0.0, min(100.0, score))

    # Risk level thresholds
    if score >= 70:
        risk_level = RiskLevel.LOW
    elif score >= 40:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.HIGH

    return KYCRiskScore(overall_score=score, risk_level=risk_level, factors=factors)
