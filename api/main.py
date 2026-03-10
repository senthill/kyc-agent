"""KYC Agent REST API"""
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import json

from models.kyc import KYCCase, KYCStatus, CustomerData
from agent.orchestrator import kyc_graph

app = FastAPI(
    title="KYC Agent API",
    description="AI-powered KYC verification agent",
    version="0.1.0"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/kyc/cases")
async def create_kyc_case(
    customer_data: str = Form(...),
    id_document: UploadFile = File(...),
    selfie: UploadFile = File(None),
    proof_of_address: UploadFile = File(None),
):
    """Submit a new KYC case for verification."""
    customer = CustomerData(**json.loads(customer_data))
    case_id = str(uuid.uuid4())

    # TODO: Upload documents to S3 and store refs
    # For now, just create the case
    case = KYCCase(case_id=case_id, customer=customer)

    # Run the KYC agent workflow
    result = await kyc_graph.ainvoke({
        "case": case,
        "messages": [],
        "next_step": "extract_documents"
    })

    final_case: KYCCase = result["case"]

    return JSONResponse({
        "case_id": final_case.case_id,
        "status": final_case.status,
        "risk_level": final_case.risk_score.risk_level if final_case.risk_score else None,
        "risk_score": final_case.risk_score.overall_score if final_case.risk_score else None,
        "decision_reason": final_case.decision_reason,
        "workflow_log": [str(m.content) for m in result["messages"]]
    })


@app.get("/kyc/cases/{case_id}")
async def get_kyc_case(case_id: str):
    """Get KYC case status and results."""
    # TODO: Fetch from DB
    return {"case_id": case_id, "message": "DB integration pending"}
