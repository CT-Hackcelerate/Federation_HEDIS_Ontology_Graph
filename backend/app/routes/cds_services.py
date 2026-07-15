"""
CDS Hooks service endpoints.
Implements CDS Hooks specification for discovery and service invocation.
"""

from fastapi import APIRouter, Depends
from typing import List
import logging

from app.schemas.cds_hooks import (
    CDSServiceDiscoveryResponse,
    CDSService,
    CDSHookRequest,
    CDSHookResponse,
    CDSCard,
    CDSSource,
)
from app.services.patient_info_service import PatientInfoService
from app.core.security import verify_any_auth
from app.core.exceptions import ServiceNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)

# Service registry - defines available CDS services
CDS_SERVICES = {
    "patient-info-by-id": CDSService(
        hook="patient-view",
        id="patient-info-by-id",
        title="Patient Information Service",
        description="Retrieves clinical decision support information for a patient based on their ID",
        prefetch={
            "patient": "Patient/{{context.patientId}}"
        },
    ),
}


@router.get("/cds-services", response_model=CDSServiceDiscoveryResponse, response_model_exclude_none=True)
async def discover_services() -> CDSServiceDiscoveryResponse:
    """
    CDS Hooks Discovery Endpoint.
    Returns a list of available CDS services per CDS Hooks specification.
    EHR systems call this endpoint to discover available services.
    """
    logger.info("CDS service discovery requested")
    
    return CDSServiceDiscoveryResponse(
        services=list(CDS_SERVICES.values())
    )


@router.post(
    "/cds-services/{service_id}",
    response_model=CDSHookResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(verify_any_auth)],
)
async def invoke_service(
    service_id: str,
    request: CDSHookRequest,
) -> CDSHookResponse:
    """
    CDS Hooks Service Invocation Endpoint.
    
    Accepts a CDS Hook request from an EHR system and returns
    decision support cards.
    
    Per CDS Hooks specification:
    - hook: The hook that triggered this request
    - hookInstance: Unique ID for this hook invocation
    - context: Hook-specific context data (includes patientId)
    - prefetch: Optional pre-fetched FHIR resources
    
    Response always contains "cards" array per specification.
    """
    # Log service invocation (no PHI)
    logger.info(f"CDS service invoked: {service_id}, hook: {request.hook}")
    
    # Validate service exists
    if service_id not in CDS_SERVICES:
        raise ServiceNotFoundException(service_id)
    
    # Route to appropriate service handler
    if service_id == "patient-info-by-id":
        service = PatientInfoService()
        cards = await service.process_request(request)
        return CDSHookResponse(cards=cards)
    
    # Default: return empty cards for unknown services
    return CDSHookResponse(cards=[])
