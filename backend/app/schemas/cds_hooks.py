"""
CDS Hooks Pydantic schemas.
Implements CDS Hooks specification models for request/response validation.
See: https://cds-hooks.hl7.org/2.0/
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Optional, Any
from enum import Enum


class Indicator(str, Enum):
    """
    CDS Card indicator values per specification.
    - info: Informational, no action needed
    - warning: Warning, attention may be needed
    - critical: Critical, action required
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CDSSource(BaseModel):
    """
    Source of the CDS card information.
    Required field per CDS Hooks specification.
    """
    label: str = Field(..., description="Display label for the source")
    url: Optional[str] = Field(None, description="URL to learn more about the source")
    icon: Optional[str] = Field(None, description="URL to an icon for the source")
    
    class Config:
        # Exclude None values from serialization
        json_encoders = {type(None): lambda _: ...}
    
    def model_dump(self, **kwargs):
        # Remove None fields per CDS Hooks requirement
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class CDSLink(BaseModel):
    """
    Link for CDS card actions.
    Allows EHR to provide navigation to external resources.
    """
    label: str = Field(..., description="Display label for the link")
    url: str = Field(..., description="URL to navigate to")
    type: str = Field(default="absolute", description="Link type: absolute or smart")
    appContext: Optional[str] = Field(None, description="SMART app context")
    
    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class CDSSuggestion(BaseModel):
    """
    Suggestion for automated actions.
    Allows EHR to offer quick actions to users.
    """
    label: str = Field(..., description="Display label for the suggestion")
    uuid: Optional[str] = Field(None, description="Unique identifier for tracking")
    isRecommended: Optional[bool] = Field(None, description="Whether this is recommended")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="FHIR actions to perform")
    
    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class CDSCard(BaseModel):
    """
    CDS Hooks Card - the primary response unit.
    
    Required fields per specification:
    - summary: One-line summary of the card
    - indicator: info | warning | critical
    - source: Information about the source
    
    Optional fields:
    - detail: Detailed markdown content
    - suggestions: Automated actions
    - links: External resources
    """
    summary: str = Field(
        ..., 
        description="One-liner summary of the card",
        max_length=140,
    )
    indicator: Indicator = Field(
        ...,
        description="Urgency/importance indicator",
    )
    source: CDSSource = Field(
        ...,
        description="Source of the information",
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed information in markdown",
    )
    suggestions: Optional[List[CDSSuggestion]] = Field(
        None,
        description="Suggested automated actions",
    )
    links: Optional[List[CDSLink]] = Field(
        None,
        description="Links to external resources",
    )
    overrideReasons: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Reasons for overriding this card",
    )
    selectionBehavior: Optional[str] = Field(
        None,
        description="How suggestions should be selected",
    )
    
    def model_dump(self, **kwargs):
        # Never include null fields per CDS Hooks requirement
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class CDSHookContext(BaseModel):
    """
    CDS Hook context - varies by hook type.
    For patient-view hook, contains patientId.
    """
    patientId: Optional[str] = Field(None, description="Patient ID from EHR")
    userId: Optional[str] = Field(None, description="User ID from EHR")
    encounterId: Optional[str] = Field(None, description="Encounter ID if applicable")
    
    # Allow additional context fields for different hooks
    class Config:
        extra = "allow"


class CDSHookRequest(BaseModel):
    """
    CDS Hooks service invocation request.
    
    Required fields:
    - hook: The hook that triggered this request (e.g., "patient-view")
    - hookInstance: Unique UUID for this hook invocation
    - context: Hook-specific context data
    
    Optional fields:
    - prefetch: Pre-fetched FHIR resources
    - fhirServer: FHIR server URL for additional queries
    - fhirAuthorization: OAuth2 token for FHIR access
    """
    hook: str = Field(
        ...,
        description="The hook that triggered this CDS request",
    )
    hookInstance: str = Field(
        ...,
        description="Unique identifier for this hook invocation",
    )
    context: CDSHookContext = Field(
        ...,
        description="Hook-specific context data",
    )
    prefetch: Optional[Dict[str, Any]] = Field(
        None,
        description="Pre-fetched FHIR resources",
    )
    fhirServer: Optional[str] = Field(
        None,
        description="Base URL of the EHR's FHIR server",
    )
    fhirAuthorization: Optional[Dict[str, str]] = Field(
        None,
        description="OAuth2 authorization for FHIR access",
    )
    
    @field_validator("hook")
    @classmethod
    def validate_hook(cls, v: str) -> str:
        """Validate hook name format."""
        if not v or not v.strip():
            raise ValueError("Hook name cannot be empty")
        return v.strip()
    
    @field_validator("hookInstance")
    @classmethod
    def validate_hook_instance(cls, v: str) -> str:
        """Validate hookInstance is provided."""
        if not v or not v.strip():
            raise ValueError("hookInstance cannot be empty")
        return v.strip()


class CDSHookResponse(BaseModel):
    """
    CDS Hooks service response.
    Always contains cards array per specification.
    """
    cards: List[CDSCard] = Field(
        default_factory=list,
        description="Array of CDS cards to display",
    )
    
    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class CDSService(BaseModel):
    """
    CDS Service definition for discovery endpoint.
    """
    hook: str = Field(..., description="The hook this service responds to")
    id: str = Field(..., description="Unique identifier for the service")
    title: str = Field(..., description="Human-readable service name")
    description: str = Field(..., description="Description of the service")
    prefetch: Optional[Dict[str, str]] = Field(
        None,
        description="Prefetch templates for FHIR queries",
    )
    usageRequirements: Optional[str] = Field(
        None,
        description="Human-readable usage requirements",
    )
    
    model_config = {"json_schema_serialization_defaults_required": True}
    
    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)
        return super().model_dump(**kwargs)


class CDSServiceDiscoveryResponse(BaseModel):
    """
    Response for CDS services discovery endpoint.
    Contains array of available services.
    """
    services: List[CDSService] = Field(
        ...,
        description="Array of available CDS services",
    )
