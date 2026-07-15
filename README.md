# EHR Care Gap Detection Platform

## Executive Summary

The **EHR Care Gap Detection Platform** is a production-ready, standards-compliant Clinical Decision Support (CDS) system that identifies and surfaces patient care gaps to clinicians at the point of care. Built on HL7 CDS Hooks 2.0 specification and FHIR standards, this platform bridges the gap between healthcare data lakes and EHR systems, enabling real-time clinical insights.

### Key Value Proposition

| Capability | Description |
|------------|-------------|
| **Real-time Care Gap Detection** | Retrieves patient-specific care gaps (HEDIS, preventive screenings, chronic disease management) from Databricks Lakebase |
| **Standards-Compliant API** | CDS Hooks 2.0 compliant endpoints for seamless EHR integration |
| **Plug-and-Play Frontend** | Embeddable microfrontend for rapid deployment in any EHR environment |
| **Enterprise Data Integration** | Direct connectivity to Databricks Unity Catalog & Delta Lake |
| **HIPAA-Ready Architecture** | PHI-safe logging, compliant error handling, secure authentication |

---
<br>

### Application Demo - Microfrontend Look & Feel

<div align="center">

![EHR Care Gap Detection Platform Demo](projectDemo/Federated_Hedis_Ontology_Graph_Demo_GIF.gif)

📥 **[Download Full Demo Video (MP4)](projectDemo/Federated_Hedis_Ontology_Graph_Demo_Video.mp4)**

</div>

---

### Future Monetization Roadmap

The platform is designed with a **dual-channel monetization strategy** targeting healthcare payers, EHR vendors, and health systems:

#### Channel 1: API-as-a-Service (B2B SaaS)

**Value Drivers:**
- FHIR-compliant payload control gives integrating payers complete data sovereignty
- CDS Hooks standard ensures zero custom integration work for EHR vendors
- Multi-tenant architecture supports white-label deployment for enterprise clients

#### Channel 2: Embeddable Microfrontend (Iframe Integration)

**Value Drivers:**
- Single iframe embed works with EHR systems of any maturity level
- No backend changes required—pure frontend integration
- Responsive design adapts to any EHR viewport

<br>

## Summary of Features

### Backend Features

| Feature | Technology | Description |
|---------|------------|-------------|
| **CDS Hooks API** | FastAPI | Full CDS Hooks 2.0 discovery and invocation endpoints |
| **Care Gap Detection** | Python | Clinical rules engine for HEDIS/preventive care gap identification |
| **Databricks Integration** | Lakebase PostgreSQL | Direct connection to Unity Catalog via PostgreSQL wire protocol |
| **Flexible Data Sources** | Repository Pattern | Supports Databricks, Parquet files, and mock data |
| **Security** | API Key + Bearer Token | Dual authentication with PHI-safe logging |
| **HIPAA Compliance** | Exception Handling | All errors return compliant empty responses; no PHI in logs |
| **API Documentation** | OpenAPI/Swagger | Auto-generated interactive documentation |
| **Production Ready** | Gunicorn + uvicorn | ASGI deployment with worker configuration |

### Frontend Features

| Feature | Technology | Description |
|---------|------------|-------------|
| **Patient Lookup** | React + Redux | Real-time patient search with FHIR resource retrieval |
| **Care Gap Dashboard** | Material-UI | Visual display of care gaps with severity indicators |
| **CDS Card Rendering** | React Components | Standards-compliant rendering of CDS Hooks cards |
| **Indicator System** | Color-coded Alerts | Critical/Warning/Info visual hierarchy |
| **Responsive Design** | CSS Grid + Flexbox | Adapts to any EHR viewport size |
| **Theme System** | MUI Theming | Customizable look-and-feel for white-label deployments |
| **Iframe-Ready** | Standalone Build | Single bundle deployment for microfrontend integration |

---

<br>

## CDS Hooks and FHIR Standards Enforcement

This platform strictly adheres to HL7 interoperability standards to ensure seamless EHR integration:

### CDS Hooks 2.0 Compliance

| Specification Element | Implementation |
|-----------------------|----------------|
| **Discovery Endpoint** | `GET /cds-services` returns service catalog per spec |
| **Service Invocation** | `POST /cds-services/{patientId}` accepts hook requests |
| **Hook Types** | Supports `patient-view` hook with context binding |
| **Card Response** | Returns `cards[]` with required `summary`, `indicator`, `source` |
| **Prefetch Templates** | Declares `Patient/{{context.patientId}}` prefetch |
| **Error Handling** | Returns empty `cards[]` on errors (never exposes internals) |

### CDS Card Indicators

```
┌─────────────┬───────────────────────────────────────────┐
│  critical   │ Immediate action required (red)          │
│  warning    │ Attention needed (orange)                │
│  info       │ Informational only (blue)                │
└─────────────┴───────────────────────────────────────────┘
```

### FHIR R4 Compatibility

| FHIR Element | Usage |
|--------------|-------|
| **Patient Resource** | Retrieved via `GET /Patient/{id}` for demographics |
| **Prefetch Specification** | FHIR resource paths in CDS service definition |
| **Context Binding** | `{{context.patientId}}` templating per CDS Hooks spec |
| **Resource References** | Support for FHIR reference resolution in responses |

### Sample CDS Request/Response

**Request:**
```json
{
  "hook": "patient-view",
  "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
  "context": {
    "patientId": "224369000000000"
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
      "detail": "**Gap Type:** HEDIS\n\n**Recommended Action:** Schedule annual wellness visit"
    }
  ]
}
```

---
<br>

## Databricks Integration: API to Lakebase

The platform connects to Databricks Lakebase (Unity Catalog + Delta Lake) via the PostgreSQL wire protocol, enabling enterprise-grade data access:

### Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────────────┐
│   EHR System     │ ───► │   CDS API        │ ───► │   Databricks Lakebase    │
│   (CDS Client)   │      │   (FastAPI)      │      │   (Unity Catalog)        │
└──────────────────┘      └──────────────────┘      └──────────────────────────┘
        │                         │                          │
        │  CDS Hooks 2.0          │  PostgreSQL Protocol     │  Delta Lake
        │  patient-view hook      │  PAT Authentication      │  input_hackathon table
```

### Lakebase Configuration

| Parameter | Environment Variable | Description |
|-----------|---------------------|-------------|
| Host | `LAKEBASE_POSTGRES_HOST` | Databricks SQL Warehouse endpoint |
| Port | `LAKEBASE_POSTGRES_PORT` | Default: 5432 |
| Database | `LAKEBASE_POSTGRES_DATABASE` | Unity Catalog database |
| Schema | `LAKEBASE_POSTGRES_SCHEMA` | Target schema (default: `public`) |
| Table | `LAKEBASE_POSTGRES_TABLE` | Care gap table (`input_hackathon`) |
| Authentication | `LAKEBASE_POSTGRES_PASSWORD` | Databricks Personal Access Token (PAT) |

### Data Schema: `input_hackathon`

```sql
-- Care gap data structure from Databricks
patient_id          STRING      -- Patient identifier (EHR context)
patient_ssui        BIGINT      -- Patient SSUI
mbi_id              STRING      -- Medicare Beneficiary ID
mbi_number          STRING      -- MBI Number
gap_type            STRING      -- Gap category (HEDIS, Preventive, etc.)
gap_type_description STRING     -- Human-readable gap description
gap_action          STRING      -- Recommended clinical action
gap_code_description STRING     -- Measure code description
gap_summary         STRING      -- Summary for CDS card display
```

### Flexible Data Sources

The repository layer supports multiple data backends for different deployment scenarios:

| Mode | Use Case | Configuration |
|------|----------|---------------|
| **Mock Data** | Development/Testing | `USE_MOCK_DATA=true` |
| **Databricks Lakebase** | Production | Configure `LAKEBASE_POSTGRES_*` vars |
| **Local Parquet** | Offline/Edge | Configure `PARQUET_DATA_PATH` |

---

<br>

## Integration Guidance

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd hackathon2026_ehr_gap_poc

# Start Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Detailed Documentation

| Component | Documentation | Description |
|-----------|---------------|-------------|
| **Backend API** | [backend/README.md](backend/README.md) | API endpoints, configuration, deployment |
| **Frontend App** | [frontend/README.md](frontend/README.md) | React components, build process, customization |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check for load balancers/monitoring |
| `/cds-services` | GET | CDS Hooks discovery endpoint |
| `/cds-services/patient-info-by-id` | POST | CDS Hooks service invocation |
| `/docs` | GET | Interactive Swagger documentation |

### Frontend Integration (Iframe Embed)

```html
<!-- Embed the care gap dashboard in any EHR -->
<iframe 
  src="https://your-deployment.com/?patientId=12345" 
  width="100%" 
  height="600px"
  frameborder="0">
</iframe>
```

---
<br>

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI (Python 3.10+) |
| **Frontend Framework** | React 18 + Redux |
| **UI Components** | Material-UI (MUI) v5 |
| **Data Layer** | Databricks Lakebase / PostgreSQL |
| **Build Tools** | Webpack 5, Babel |
| **API Specification** | OpenAPI 3.0 / Swagger |
| **Deployment** | Gunicorn + uvicorn (ASGI) |

---

<div align="center">

---

⚠️ **INTERNAL USE ONLY** ⚠️

This service in its current form is strictly meant for internal use and should be treated as **work in progress**. 

Not intended for production deployment without proper security review, compliance validation, and performance testing. All environment files are excluded from commit intentionally.

**Hackcelerate 2026 | CitiusTech**

---

</div>
