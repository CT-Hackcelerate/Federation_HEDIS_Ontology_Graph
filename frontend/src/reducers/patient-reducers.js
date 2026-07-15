import * as types from '../actions/action-types';
import { defaultPatientId } from '../config/fhir-config';

const initialState = {
  defaultPatientId,
  currentPatient: null,
  careGaps: [],
  apiMetadata: null,
};

const patientReducers = (state = initialState, action) => {
  switch (action.type) {
    // Store the patient info from a successful API call
    case types.GET_PATIENT_SUCCESS: {
      const { patient } = action;
      const newPatient = {
        id: patient.id,
        name: patient.name || `Patient ${patient.id}`,
      };
      return { ...state, currentPatient: newPatient };
    }

    // Clear the patient in context on a failed retrieval
    case types.GET_PATIENT_FAILURE: {
      return { ...state, currentPatient: null, careGaps: [], apiMetadata: null };
    }

    // Store care gap cards from the CDS API response
    case types.SET_CARE_GAPS: {
      return { ...state, careGaps: action.cards || [] };
    }

    // Store API metadata for footer display
    case types.SET_API_METADATA: {
      return { ...state, apiMetadata: action.metadata };
    }

    default:
      return state;
  }
};

export default patientReducers;
