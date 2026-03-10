"""Document OCR & data extraction tool."""
# TODO: Integrate AWS Textract or Google Document AI
from models.kyc import DocumentExtractionResult


async def extract_document_data(case_id: str) -> DocumentExtractionResult:
    """Extract structured data from identity documents."""
    # Stub — replace with real OCR integration
    raise NotImplementedError("OCR integration pending")
