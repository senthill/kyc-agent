"""
Document OCR & data extraction tool.
Uses EasyOCR for text extraction + LLM for structured parsing.
"""
import re
import asyncio
from pathlib import Path
from typing import Optional
import easyocr
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

from models.kyc import DocumentExtractionResult

# Initialize EasyOCR reader (English + common Asian languages for SG market)
# Loaded once at startup — takes ~10s first time (downloads models)
_reader: Optional[easyocr.Reader] = None


def get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(
            ["en", "ch_sim", "ch_tra", "ms"],  # English, Simplified/Traditional Chinese, Malay
            gpu=False  # Set True if GPU available
        )
    return _reader


PARSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a KYC document parser. Given raw OCR text from an identity document, 
extract structured fields. Return ONLY valid JSON with these fields:
- document_type: one of [passport, national_id, driving_license, unknown]
- full_name: string or null
- dob: string in YYYY-MM-DD format or null
- document_number: string or null
- expiry_date: string in YYYY-MM-DD format or null
- nationality: string (ISO country code) or null
- confidence: float 0.0-1.0 based on how complete/clear the extraction is

If a field is not found, use null. Do not guess."""),
    ("human", "OCR text:\n\n{ocr_text}"),
])


async def extract_document_data(case_id: str, image_path: str) -> DocumentExtractionResult:
    """
    Extract structured data from an identity document image.
    
    Steps:
    1. Run EasyOCR to get raw text from image
    2. Pass raw text to LLM to parse into structured fields
    """
    # Step 1: OCR
    loop = asyncio.get_event_loop()
    reader = get_reader()

    # Run blocking EasyOCR in thread pool to avoid blocking event loop
    results = await loop.run_in_executor(
        None,
        lambda: reader.readtext(image_path, detail=1, paragraph=False)
    )

    # Concatenate text blocks, filtering low-confidence noise
    raw_text = "\n".join(
        text for (_, text, conf) in results if conf > 0.3
    )

    if not raw_text.strip():
        return DocumentExtractionResult(
            document_type="unknown",
            confidence=0.0
        )

    # Step 2: LLM structured parsing
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = PARSE_PROMPT | llm

    response = await chain.ainvoke({"ocr_text": raw_text})

    import json
    try:
        parsed = json.loads(response.content)
        return DocumentExtractionResult(**parsed)
    except Exception:
        # Fallback: return raw with low confidence
        return DocumentExtractionResult(
            document_type="unknown",
            confidence=0.2
        )


def preprocess_image(image_path: str) -> str:
    """
    Optional preprocessing to improve OCR accuracy.
    Deskew, denoise, increase contrast.
    Returns path to preprocessed image.
    """
    try:
        import cv2
        import numpy as np

        img = cv2.imread(image_path)
        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        # Adaptive threshold for better contrast
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        out_path = image_path.replace(".", "_processed.")
        cv2.imwrite(out_path, thresh)
        return out_path
    except Exception:
        return image_path  # Return original if preprocessing fails
