"""
Patient Information CDS Service.
Processes patient-view hook requests and returns clinical decision support cards.
"""

from typing import List, Optional
import logging

from app.schemas.cds_hooks import (
    CDSHookRequest,
    CDSCard,
    CDSSource,
    Indicator,
)
from app.repositories.lakebase_repository import LakebaseRepository

logger = logging.getLogger(__name__)


class PatientInfoService:
    """
    Service for processing patient-info-by-id CDS requests.
    
    Retrieves patient data from Lakebase/Parquet and generates
    appropriate CDS cards based on clinical rules.
    """
    
    def __init__(self):
        self.repository = LakebaseRepository()
        self.source = CDSSource(
            label="Clinical Decision Support System"
        )
    
    async def process_request(self, request: CDSHookRequest) -> List[CDSCard]:
        """
        Process CDS Hook request and return cards.
        
        Args:
            request: CDS Hook request containing patient context
            
        Returns:
            List of CDS cards with clinical recommendations
        """
        # Extract patient ID from context
        patient_id = request.context.patientId
        
        if not patient_id:
            logger.warning("No patientId in request context")
            # Return empty cards per CDS Hooks spec (don't expose internal errors)
            return []
        
        # Log request processing (no PHI - just IDs)
        logger.info(f"Processing patient-info request for ID: {patient_id[:8]}...")
        
        try:
            # Fetch patient clinical data from repository
            patient_data = await self.repository.get_patient_data(patient_id)
            
            if not patient_data:
                # No data found - return empty cards
                logger.info(f"No clinical data found for patient")
                return []
            
            # Generate cards based on clinical rules
            cards = await self._generate_cards(patient_data)
            
            logger.info(f"Generated {len(cards)} cards for request")
            return cards
            
        except Exception as e:
            # Log error without PHI
            logger.error(f"Error processing patient request: {type(e).__name__}")
            # Return empty cards - never expose internal errors
            return []
    
    async def _generate_cards(self, patient_data: dict) -> List[CDSCard]:
        """
        Generate CDS cards based on patient clinical data.
        
        Implements clinical decision rules to determine appropriate
        recommendations and their urgency levels.
        """
        cards: List[CDSCard] = []
        
        gaps = patient_data.get("gaps", [])
        for gap in gaps:
            card = self._create_gap_card(gap)
            if card:
                cards.append(card)
        
        return cards
    
    def _create_gap_card(self, gap: dict) -> Optional[CDSCard]:
        """
        Create a CDS card for a care gap.
        
        Args:
            gap: Dictionary containing gap information from input_hackathon table
                - gap_type: Type of gap (e.g., HEDIS, Preventive)
                - gap_type_description: Description of the gap type
                - gap_action: Recommended action to close the gap
                - gap_code_description: Code description
                - gap_summary: Summary of the gap
        
        Returns:
            CDSCard with gap information
        """
        gap_type = gap.get("gap_type", "Care Gap")
        gap_type_description = gap.get("gap_type_description", "")
        gap_action = gap.get("gap_action", "")
        gap_code_description = gap.get("gap_code_description", "")
        gap_summary = gap.get("gap_summary", "")
        
        # Use gap_summary as the card summary, fallback to gap_type_description
        summary = gap_summary or gap_type_description or f"{gap_type} gap identified"
        
        # Build detailed markdown content
        detail_parts = []
        if gap_type:
            detail_parts.append(f"**Gap Type:** {gap_type}")
        if gap_type_description:
            detail_parts.append(f"**Description:** {gap_type_description}")
        if gap_action:
            detail_parts.append(f"**Recommended Action:** {gap_action}")
        if gap_code_description:
            detail_parts.append(f"**Code:** {gap_code_description}")
        
        detail = "\n\n".join(detail_parts) if detail_parts else None
        
        return CDSCard(
            summary=summary[:140],  # Truncate to CDS Hooks max length
            indicator=Indicator.WARNING,
            source=self.source,
            detail=detail,
        )
