# KYC Agent 🏦🤖

An AI-powered KYC (Know Your Customer) Agent that automates the full lifecycle of bank KYC verification — from document collection to risk decisioning — replicating what human KYC analysts do, at scale.

## What It Does

- **Document Ingestion** — Accept ID docs, proof of address, selfies, bank statements
- **OCR & Extraction** — Extract structured data from passports, national IDs, utility bills
- **Liveness & Face Match** — Verify selfie matches ID photo, detect spoofing
- **Document Authenticity** — Detect tampered/forged documents
- **Identity Verification** — Cross-check extracted data against external databases
- **Sanctions & PEP Screening** — Screen against OFAC, UN, EU, PEP lists
- **Adverse Media Check** — NLP scan of news for negative mentions
- **Risk Scoring** — Produce a composite KYC risk score (Low / Medium / High)
- **Decision & Escalation** — Auto-approve low risk; escalate edge cases to human review
- **Ongoing Monitoring** — Trigger re-KYC when customer behavior changes

## Architecture

```
kyc-agent/
├── agent/              # Core AI agent logic
│   ├── orchestrator.py # Main KYC workflow orchestrator
│   ├── tools/          # Agent tools (one per capability)
│   └── prompts/        # LLM prompt templates
├── api/                # FastAPI REST endpoints
├── services/           # External service integrations
│   ├── ocr.py          # Document OCR (AWS Textract / Google Vision)
│   ├── liveness.py     # Face match & liveness detection
│   ├── sanctions.py    # Sanctions & PEP screening
│   ├── adverse_media.py# Adverse media NLP
│   └── database.py     # Customer & case storage
├── models/             # Pydantic data models
├── config/             # Config & environment
├── tests/              # Unit & integration tests
└── docs/               # Architecture & API docs
```

## Tech Stack

- **Agent Framework:** LangGraph (stateful multi-step agent)
- **LLM:** OpenAI GPT-4o / Anthropic Claude
- **OCR:** AWS Textract or Google Document AI
- **Face Match:** AWS Rekognition or DeepFace
- **Database:** PostgreSQL + pgvector (for embeddings)
- **API:** FastAPI
- **Queue:** Redis / Celery (async doc processing)
- **Storage:** S3-compatible (documents)

## Quick Start

```bash
# Clone and install
git clone https://github.com/senthill/kyc-agent.git
cd kyc-agent
pip install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
# Edit .env with your API keys

# Run the API
uvicorn api.main:app --reload

# Submit a KYC case
curl -X POST http://localhost:8000/kyc/cases \
  -F "id_document=@passport.jpg" \
  -F "selfie=@selfie.jpg" \
  -F "customer_data={\"name\":\"John Doe\",\"dob\":\"1990-01-01\"}"
```

## KYC Workflow

```
Customer Submission
       ↓
Document Ingestion & OCR
       ↓
Liveness & Face Match
       ↓
Document Authenticity Check
       ↓
Data Validation & Cross-check
       ↓
Sanctions / PEP Screening
       ↓
Adverse Media Scan
       ↓
Risk Score Calculation
       ↓
Auto-Decision (Low Risk) → Approved ✅
       ↓
Escalation (Medium/High Risk) → Human Review 👤
```

## Status

🚧 In active development

## License

MIT
