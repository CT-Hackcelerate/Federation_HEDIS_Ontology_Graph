import { cdsApiBaseUrl } from '../config/fhir-config';

/**
 * Stores the CDS API base URL for display in the UI.
 */
const initialState = {
  currentFhirServer: cdsApiBaseUrl,
  defaultFhirServer: cdsApiBaseUrl,
};

const fhirServerReducers = (state = initialState) => state;

export default fhirServerReducers;
