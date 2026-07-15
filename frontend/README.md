# Patient Details POC (`sandbox-master-POC`)

A trimmed-down proof-of-concept derived from the [CDS Hooks Sandbox](../sandbox-master) EHR front end.
It keeps the same technology stack and architecture (React + Redux + MUI + axios + webpack) but strips
everything down to a **single screen**: enter a patient ID, send an API request to a FHIR server, and
display the returned patient details.

## What it does

1. On load (and on every lookup) the front end sends `GET {fhirServer}/Patient/{patientId}` to the
   configured FHIR server.
2. The FHIR `Patient` resource in the response is normalized and shown on screen (name, ID, gender,
   birth date, marital status, phone, email, address).
3. A patient-ID input lets you fetch any other patient from the same server. You can also pre-load a
   patient via the `patientId` URL query parameter (e.g. `http://localhost:8080/?patientId=smart-1288992`).

The FHIR server is fixed to an open (unsecured) DSTU2 endpoint and configured in
[`src/config/fhir-config.js`](src/config/fhir-config.js), along with the default patient ID.

## How it maps to the original Sandbox

This POC reuses the original Sandbox's patterns so it is recognizably "the same app, trimmed":

| Concern | Original Sandbox | POC |
| --- | --- | --- |
| Data fetch | `src/retrieve-data-helpers/patient-retrieval.js` | same file, trimmed to a single `GET /Patient/{id}` |
| State | Redux store + actions + reducers | `patientState`, `fhirServerState`, `uiState` slices |
| Patient screen | `components/PatientView` | `components/PatientView` (details card) |
| Patient ID entry | `components/PatientEntry` (modal + select) | `components/PatientLookup` (inline field) |
| Theme | `src/theme/index.js` (MUI) | same theme |

Everything related to CDS Services, hooks, cards, Rx/PAMA views, SMART launch, and card demos has been
removed, since the POC only exercises the single patient request/response flow.

## Run it

```
npm install
npm run dev
```

Then open <http://localhost:8080>. A production build can be produced with `npm run build`.
