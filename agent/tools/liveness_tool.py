"""Liveness detection & face match tool."""
# TODO: Integrate AWS Rekognition or DeepFace
from models.kyc import LivenessResult


async def verify_liveness(case_id: str) -> LivenessResult:
    """Verify selfie liveness and match against ID photo."""
    raise NotImplementedError("Liveness integration pending")
