"""Sanctions & PEP screening tool."""
# TODO: Integrate OpenSanctions or ComplyAdvantage
from models.kyc import SanctionsResult


async def screen_sanctions(name: str, dob: str) -> SanctionsResult:
    """Screen customer against sanctions lists and PEP databases."""
    raise NotImplementedError("Sanctions screening integration pending")
