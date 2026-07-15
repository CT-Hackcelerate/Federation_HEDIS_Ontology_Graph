/**
 * Default configuration for the EHR Care Gap Dashboard.
 *
 * This application connects to the local CDS Hooks API to retrieve patient care gap
 * information. The API endpoint exposes CDS services compatible with CDS Hooks specification.
 */
export const cdsApiBaseUrl = 'http://localhost:8000';
export const cdsServiceId = 'patient-info-by-id';
export const defaultPatientId = '';
export const appVersion = '1.0.0';
