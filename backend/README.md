# Clinical Decision Support (CDS) API

## Executive Summary

The CDS API is a **CDS Hooks 2.0 compliant** Clinical Decision Support service designed to integrate with Electronic Health Record (EHR) systems. It identifies and surfaces **care gaps** (e.g., overdue screenings, wellness visits, lab tests) to clinicians at the point of care via standardized CDS cards.

**Key Capabilities:**
- **Real-time Care Gap Detection**: Retrieves patient-specific care gaps from Databricks Lakebase/PostgreSQL
- **EHR Integration Ready**: Implements HL7 CDS Hooks specification for seamless EHR integration
- **Flexible Data Sources**: Supports Databricks Lakebase, PostgreSQL, Parquet files, and mock data
- **Security**: API key and Bearer token authentication with PHI-safe logging
- **HIPAA Considerations**: No PHI/PII logged; all errors return compliant empty responses

---

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check for load balancers/monitoring |
| `/cds-services` | GET | CDS Hooks discovery endpoint |
| `/cds-services/{patientId}` | POST | CDS Hooks service invocation |

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Running the Server

```bash
# Development
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
gunicorn -c gunicorn_conf.py app.main:app
```

### Environment Configuration

Create a `.env` file:

```env
ENVIRONMENT=development
USE_MOCK_DATA=true  --Mock data for testing without active API connection.

Lakebase/PostgreSQL (when USE_MOCK_DATA=false) 
LAKEBASE_POSTGRES_HOST=your-host
LAKEBASE_POSTGRES_PORT=5432
LAKEBASE_POSTGRES_DATABASE=your-db
LAKEBASE_POSTGRES_USER=your-user
LAKEBASE_POSTGRES_PASSWORD=your-pat-token

# Security
API_KEY=your-api-key
BEARER_TOKEN_SECRET=your-secret
```

---

## API Behavior

### 1. Service Discovery (`GET /cds-services`)

Returns available CDS services per CDS Hooks specification.

**Response:**
```json
{
  "services": [
    {
      "hook": "patient-view",
      "id": "patient-info-by-id",
      "title": "Patient Information Service",
      "description": "Retrieves clinical decision support information for a patient based on their ID",
      "prefetch": {
        "patient": "Patient/{{context.patientId}}"
      }
    }
  ]
}
```

### 2. Service Invocation (`POST /cds-services/patient-info-by-id`)

Processes patient context and returns care gap cards.

**Request:**
```json
{
  "hook": "patient-view",
  "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
  "context": {
    "patientId": "1001"
  }
}
```

**Response:**
```json
{
  "cards": [
    {
      "summary": "Patient is due for annual wellness visit",
      "indicator": "warning",
      "source": {
        "label": "Clinical Decision Support System"
      },
      "detail": "**Gap Type:** HEDIS\n\n**Description:** Annual Wellness Visit\n\n**Recommended Action:** Schedule annual wellness visit\n\n**Code:** AWV - Annual Wellness Visit"
    }
  ]
}
```

### Card Indicators

| Indicator | Meaning |
|-----------|---------|
| `info` | Informational, no action needed |
| `warning` | Attention may be needed |
| `critical` | Action required |

### Error Handling

All errors return CDS-compliant responses with empty cards array:

```json
{
  "cards": []
}
```

Internal error details are **never** exposed to EHR systems.

> **Note:** HTTP failure status codes (4xx/5xx) are intentionally suppressed by design given the limited internal usage of this POC API; all error scenarios deterministically return FHIR-compliant empty `{"cards": []}` responses.

### Authentication

- **Development Mode**: Authentication bypassed when credentials not configured
- **Production Mode**: Requires either:
  - `X-API-Key` header with valid API key, OR
  - `Authorization: Bearer <token>` header

---

## Data Schema

The API expects patient data with care gaps in this structure:

```json
{
  "patient_id": "1001",
  "patient_ssui": 123456789,
  "mbi_id": "MBI001",
  "mbi_number": "1EG4-TE5-MK72",
  "gaps": [
    {
      "gap_type": "HEDIS",
      "gap_type_description": "Annual Wellness Visit",
      "gap_action": "Schedule annual wellness visit",
      "gap_code_description": "AWV - Annual Wellness Visit",
      "gap_summary": "Patient is due for annual wellness visit"
    }
  ]
}
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   ├── exceptions.py       # CDS-compliant error handling
│   │   ├── logging.py          # PHI-safe logging setup
│   │   └── security.py         # API key/Bearer authentication
│   ├── routes/
│   │   ├── cds_services.py     # CDS Hooks endpoints
│   │   └── health.py           # Health check endpoint
│   ├── schemas/
│   │   └── cds_hooks.py        # Pydantic models (CDS Hooks spec)
│   ├── services/
│   │   └── patient_info_service.py  # Care gap card generation
│   └── repositories/
│       └── lakebase_repository.py   # Data access layer
├── requirements.txt
├── gunicorn_conf.py
└── .env
```

---

## Testing

```bash
# Run tests
pytest --cov=app

# Test service invocation (PowerShell)
$body = @{
    hook = "patient-view"
    hookInstance = "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea"
    context = @{ patientId = "1001" }
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/cds-services/patient-info-by-id -Method POST -Body $body -ContentType "application/json"
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |
| psycopg2 | PostgreSQL connectivity |
| PyArrow/Pandas | Parquet data processing |
| python-jose | JWT token handling |

---

## References

- [CDS Hooks Specification 2.0](https://cds-hooks.hl7.org/2.0/)
- [HL7 FHIR](https://hl7.org/fhir/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
