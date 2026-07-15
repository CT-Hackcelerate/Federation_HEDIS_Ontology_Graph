"""
Lakebase / Parquet Data Repository.

This module provides data access to clinical data stored in:
- Databricks Lakebase (Unity Catalog + Delta Lake)
- Local Parquet files (for development/testing)

Design Principles:
- Abstract data source from business logic
- Support both Databricks SQL and local Parquet
- Easily extensible for FHIR resource mapping
- No PHI in logs

To implement real Databricks connection:
1. Set USE_MOCK_DATA=false in environment
2. Configure DATABRICKS_* environment variables
3. Implement _query_databricks method with actual SQL

To implement real Parquet queries:
1. Set USE_MOCK_DATA=false
2. Configure PARQUET_DATA_PATH
3. Implement _query_parquet method with PyArrow/Pandas
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Abstract base class for data repositories."""
    
    @abstractmethod
    async def get_patient_data(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve patient clinical data by ID."""
        pass


class LakebaseRepository(BaseRepository):
    """
    Repository for accessing clinical data from Databricks Lakebase or Parquet.
    
    Supports:
    - Mock data for development
    - Databricks SQL connector for production
    - Local Parquet files for testing
    
    The repository is designed for easy extension to support:
    - FHIR resource mapping
    - Multiple data schemas
    - Caching layer
    """
    
    def __init__(self):
        self.use_mock = settings.USE_MOCK_DATA
        self.pg_host = settings.LAKEBASE_POSTGRES_HOST
        self.pg_port = settings.LAKEBASE_POSTGRES_PORT
        self.pg_database = settings.LAKEBASE_POSTGRES_DATABASE
        self.pg_user = settings.LAKEBASE_POSTGRES_USER
        self.pg_password = settings.LAKEBASE_POSTGRES_PASSWORD
        self.pg_schema = settings.LAKEBASE_POSTGRES_SCHEMA
        self.pg_table = settings.LAKEBASE_POSTGRES_TABLE
        self.parquet_path = settings.PARQUET_DATA_PATH
        
        # Connection placeholder - initialized on first use
        self._connection = None
        
        logger.info(f"LakebaseRepository initialized (mock={self.use_mock})")
    
    async def get_patient_data(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve patient clinical data by ID.
        
        Args:
            patient_id: The patient identifier from EHR context
            
        Returns:
            Dictionary containing (from input_hackathon table):
            - patient_id: Patient identifier
            - patient_ssui: Patient SSUI
            - mbi_id: Medicare Beneficiary ID
            - mbi_number: MBI Number
            - gaps: List of care gaps with:
                - gap_type, gap_type_description, gap_action,
                  gap_code_description, gap_summary
            
        Returns None if patient not found.
        """
        # Log access (no PHI - truncated ID only)
        logger.debug(f"Fetching patient data for ID: {patient_id[:8]}...")
        
        if self.use_mock:
            return await self._get_mock_data(patient_id)
        
        # Production: Route to appropriate data source
        if self.pg_host:
            return await self._query_lakebase_postgres(patient_id)
        elif self.parquet_path:
            return await self._query_parquet(patient_id)
        
        logger.warning("No data source configured")
        return None
    
    async def _get_mock_data(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Return mock clinical data for development/testing.
        
        This mock data demonstrates the expected data structure
        that matches the input_hackathon table schema.
        """
        # Sample mock data matching input_hackathon table structure
        mock_patients = {
            "1001": {
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
                        "gap_summary": "Patient is due for annual wellness visit",
                    },
                    {
                        "gap_type": "HEDIS",
                        "gap_type_description": "HbA1c Control",
                        "gap_action": "Order HbA1c test",
                        "gap_code_description": "CDC - Comprehensive Diabetes Care",
                        "gap_summary": "HbA1c test overdue for diabetic patient",
                    },
                ],
            },
            "1002": {
                "patient_id": "1002",
                "patient_ssui": 987654321,
                "mbi_id": "MBI002",
                "mbi_number": "2FH5-UF6-NL83",
                "gaps": [
                    {
                        "gap_type": "Preventive",
                        "gap_type_description": "Breast Cancer Screening",
                        "gap_action": "Schedule mammogram",
                        "gap_code_description": "BCS - Breast Cancer Screening",
                        "gap_summary": "Patient is due for breast cancer screening",
                    },
                ],
            },
        }
        
        # Return mock data or None if not found
        return mock_patients.get(patient_id)
    
    async def _query_lakebase_postgres(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Query Lakebase PostgreSQL database for patient data.
        Uses psycopg2 for PostgreSQL wire protocol connection.
        """
        import psycopg2
        
        try:
            # Connect to Lakebase PostgreSQL
            conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_database,
                user=self.pg_user,
                password=self.pg_password,
                sslmode="require"
            )
            
            with conn.cursor() as cursor:
                # Query all gaps for this patient
                query = f'''
                    SELECT 
                        DISTINCT
                        patientid,
                        "patientSSUI",
                        "MBIID",
                        "MBINumber",
                        gaptype,
                        gaptypedescription,
                        gapaction,
                        gapcodedescription,
                        gapsummary
                    FROM {self.pg_schema}.{self.pg_table}
                    WHERE patientid = %s AND gaptype is NOT NULL
                '''
                cursor.execute(query, (float(patient_id),))
                
                results = cursor.fetchall()
                
            conn.close()
            
            if not results:
                logger.info(f"No records found for patient ID: {patient_id[:8]}...")
                return None
            
            # First row for patient-level info
            first_row = results[0]
            
            # Build gaps list from all rows
            gaps = []
            for row in results:
                gaps.append({
                    "gap_type": row[4],
                    "gap_type_description": row[5],
                    "gap_action": row[6],
                    "gap_code_description": row[7],
                    "gap_summary": row[8],
                })
            
            logger.info(f"Found {len(gaps)} gap(s) for patient")
            
            return {
                "patient_id": str(int(first_row[0])) if first_row[0] else None,
                "patient_ssui": first_row[1],
                "mbi_id": first_row[2],
                "mbi_number": first_row[3],
                "gaps": gaps,
            }
        except Exception as e:
            logger.error(f"Lakebase PostgreSQL query failed: {type(e).__name__}: {e}")
            return None
    
    async def get_patient_gaps(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get care gaps for a patient."""
        data = await self.get_patient_data(patient_id)
        return data.get("gaps", []) if data else []
    
    async def get_patient_alerts(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get only alerts for a patient (legacy - returns empty)."""
        data = await self.get_patient_data(patient_id)
        return data.get("alerts", []) if data else []
    
    async def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get only conditions for a patient."""
        data = await self.get_patient_data(patient_id)
        return data.get("conditions", []) if data else []
    
    async def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get only medications for a patient."""
        data = await self.get_patient_data(patient_id)
        return data.get("medications", []) if data else []
    
    # Future FHIR Mapping Support
    # ---------------------------
    # The following methods are placeholders for FHIR resource mapping.
    # Implement these when integrating with FHIR servers or converting
    # Lakebase data to FHIR format.
    
    async def to_fhir_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Convert patient data to FHIR Patient resource format.
        Placeholder for future FHIR mapping.
        """
        # TODO: Implement FHIR Patient resource mapping
        raise NotImplementedError("FHIR mapping not yet implemented")
    
    async def to_fhir_condition(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert condition data to FHIR Condition resource format.
        Placeholder for future FHIR mapping.
        """
        # TODO: Implement FHIR Condition resource mapping
        raise NotImplementedError("FHIR mapping not yet implemented")
