"""Adverse media screening tool."""
# TODO: Integrate news APIs + NLP classification
from models.kyc import AdverseMediaResult


async def check_adverse_media(name: str) -> AdverseMediaResult:
    """Scan news and media for adverse mentions of the customer."""
    raise NotImplementedError("Adverse media integration pending")
