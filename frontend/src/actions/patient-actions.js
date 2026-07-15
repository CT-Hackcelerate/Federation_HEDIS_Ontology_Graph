import * as types from './action-types';

/**
 * Signals successful retrieval of patient data from the CDS API
 * @param patient - Patient object with basic info
 * @returns {{type, patient: *}} - Action to dispatch
 */
export function signalSuccessPatientRetrieval(patient) {
  return {
    type: types.GET_PATIENT_SUCCESS,
    patient,
  };
}

/**
 * Signals a failed retrieval of patient data from the CDS API
 * @returns {{type}} - Action to dispatch
 */
export function signalFailurePatientRetrieval() {
  return {
    type: types.GET_PATIENT_FAILURE,
  };
}

/**
 * Sets the care gaps cards received from the CDS API
 * @param {Array} cards - Array of CDS cards with care gap information
 * @returns {{type, cards: Array}} - Action to dispatch
 */
export function setCareGaps(cards) {
  return {
    type: types.SET_CARE_GAPS,
    cards,
  };
}

/**
 * Sets the API metadata for display in the footer
 * @param {Object} metadata - API response metadata (URL, response time, status, etc.)
 * @returns {{type, metadata: Object}} - Action to dispatch
 */
export function setApiMetadata(metadata) {
  return {
    type: types.SET_API_METADATA,
    metadata,
  };
}
