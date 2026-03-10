"""
KYC Agent Orchestrator
Uses LangGraph to manage stateful multi-step KYC verification workflow.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from agent.tools.ocr_tool import extract_document_data
from agent.tools.liveness_tool import verify_liveness
from agent.tools.sanctions_tool import screen_sanctions
from agent.tools.adverse_media_tool import check_adverse_media
from agent.tools.risk_scorer import calculate_risk_score
from models.kyc import KYCCase, KYCStatus, RiskLevel


class KYCState(TypedDict):
    case: KYCCase
    messages: Annotated[list, add_messages]
    next_step: str


def build_kyc_graph():
    """Build the LangGraph KYC workflow."""

    workflow = StateGraph(KYCState)

    # Add nodes
    workflow.add_node("extract_documents", extract_documents_node)
    workflow.add_node("verify_liveness", verify_liveness_node)
    workflow.add_node("screen_sanctions", screen_sanctions_node)
    workflow.add_node("check_adverse_media", check_adverse_media_node)
    workflow.add_node("calculate_risk", calculate_risk_node)
    workflow.add_node("make_decision", make_decision_node)

    # Define flow
    workflow.set_entry_point("extract_documents")
    workflow.add_edge("extract_documents", "verify_liveness")
    workflow.add_edge("verify_liveness", "screen_sanctions")
    workflow.add_edge("screen_sanctions", "check_adverse_media")
    workflow.add_edge("check_adverse_media", "calculate_risk")
    workflow.add_edge("calculate_risk", "make_decision")
    workflow.add_edge("make_decision", END)

    return workflow.compile()


async def extract_documents_node(state: KYCState) -> KYCState:
    case = state["case"]
    # image_path would come from S3 download in production
    image_path = f"/tmp/kyc/{case.case_id}/id_document.jpg"
    result = await extract_document_data(case.case_id, image_path)
    case.document_result = result
    return {"case": case, "messages": [f"✅ Document extraction complete. Confidence: {result.confidence:.0%}"]}


async def verify_liveness_node(state: KYCState) -> KYCState:
    case = state["case"]
    result = await verify_liveness(case.case_id)
    case.liveness_result = result
    status = "✅ Liveness verified" if result.is_live and not result.spoof_detected else "⚠️ Liveness check failed"
    return {"case": case, "messages": [f"{status}. Face match: {result.face_match_score:.0%}"]}


async def screen_sanctions_node(state: KYCState) -> KYCState:
    case = state["case"]
    result = await screen_sanctions(case.customer.name, case.customer.dob)
    case.sanctions_result = result
    flag = "🚨 SANCTIONS HIT" if result.is_sanctioned else ("⚠️ PEP identified" if result.is_pep else "✅ Clean")
    return {"case": case, "messages": [f"Sanctions screening: {flag}"]}


async def check_adverse_media_node(state: KYCState) -> KYCState:
    case = state["case"]
    result = await check_adverse_media(case.customer.name)
    case.adverse_media_result = result
    flag = f"⚠️ Adverse media found ({result.severity})" if result.has_adverse_media else "✅ No adverse media"
    return {"case": case, "messages": [f"Adverse media: {flag}"]}


async def calculate_risk_node(state: KYCState) -> KYCState:
    case = state["case"]
    score = calculate_risk_score(case)
    case.risk_score = score
    return {"case": case, "messages": [f"Risk score: {score.overall_score:.0f}/100 ({score.risk_level.value.upper()})"]}


async def make_decision_node(state: KYCState) -> KYCState:
    case = state["case"]
    risk = case.risk_score

    if case.sanctions_result.is_sanctioned:
        case.status = KYCStatus.REJECTED
        case.decision_reason = "Customer is on a sanctions list"
    elif risk.risk_level == RiskLevel.LOW:
        case.status = KYCStatus.APPROVED
        case.decision_reason = "Low risk — auto-approved"
    elif risk.risk_level == RiskLevel.MEDIUM:
        case.status = KYCStatus.ESCALATED
        case.decision_reason = "Medium risk — escalated for human review"
    else:
        case.status = KYCStatus.ESCALATED
        case.decision_reason = "High risk — escalated for senior analyst review"

    emoji = {"approved": "✅", "rejected": "❌", "escalated": "👤"}.get(case.status.value, "❓")
    return {"case": case, "messages": [f"{emoji} Decision: {case.status.value.upper()} — {case.decision_reason}"]}


# Singleton graph
kyc_graph = build_kyc_graph()
