import { combineReducers } from 'redux';

import patientReducers from './patient-reducers';
import fhirServerReducers from './fhir-server-reducers';
import uiReducers from './ui-reducers';

const reducers = combineReducers({
  patientState: patientReducers,
  fhirServerState: fhirServerReducers,
  uiState: uiReducers,
});

export default reducers;
