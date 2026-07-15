import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import store from '../store/store';
import { signalSuccessPatientRetrieval, signalFailurePatientRetrieval, setCareGaps, setApiMetadata } from '../actions/patient-actions';
import { setLoadingStatus, setError } from '../actions/ui-actions';
import { cdsApiBaseUrl, cdsServiceId } from '../config/fhir-config';

/**
 * Retrieve patient care gap data from the CDS API for the given patient ID and dispatch the
 * result (success or failure) to the Redux store. This sends a CDS Hooks request to the backend
 * and receives care gap cards in response.
 *
 * @param {string} patientId - The ID of the patient to fetch care gaps for
 * @returns {Promise} - Resolves with the CDS response, rejects on failure
 */
function retrievePatient(patientId) {
  return new Promise((resolve, reject) => {
    const patient = (patientId || '').trim();
    
    if (!patient) {
      store.dispatch(setError('Please enter a patient ID.'));
      return reject(new Error('No patient ID provided'));
    }

    const requestStartTime = Date.now();
    
    // Build CDS Hooks request
    const cdsRequest = {
      hook: 'patient-view',
      hookInstance: uuidv4(),
      context: {
        patientId: patient,
        userId: 'ehr-user',
      },
    };

    store.dispatch(setError(''));
    store.dispatch(setLoadingStatus(true));

    const requestUrl = `${cdsApiBaseUrl}/cds-services/${cdsServiceId}`;
    
    axios({
      method: 'post',
      url: requestUrl,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      data: cdsRequest,
    }).then((result) => {
      const responseTime = Date.now() - requestStartTime;
      store.dispatch(setLoadingStatus(false));
      
      // Store API metadata for footer display
      store.dispatch(setApiMetadata({
        requestUrl,
        responseTime,
        statusCode: result.status,
        timestamp: new Date().toISOString(),
        patientId: patient,
        cardCount: result.data?.cards?.length || 0,
      }));
      
      if (result.data && Array.isArray(result.data.cards)) {
        // Create a simple patient object from the request
        const patientObj = {
          id: patient,
          name: `Patient ${patient}`,
        };
        
        store.dispatch(signalSuccessPatientRetrieval(patientObj));
        store.dispatch(setCareGaps(result.data.cards));
        return resolve(result.data);
      }
      
      store.dispatch(signalFailurePatientRetrieval());
      store.dispatch(setError(`Invalid response from CDS API for patient "${patient}".`));
      return reject();
    }).catch((err) => {
      const responseTime = Date.now() - requestStartTime;
      console.error('Could not retrieve patient care gaps from the CDS API', err);
      store.dispatch(setLoadingStatus(false));
      store.dispatch(signalFailurePatientRetrieval());
      
      // Store error metadata
      store.dispatch(setApiMetadata({
        requestUrl,
        responseTime,
        statusCode: err.response?.status || 'N/A',
        timestamp: new Date().toISOString(),
        patientId: patient,
        error: err.message,
      }));
      
      const errorMsg = err.response?.status === 404
        ? `Patient "${patient}" not found in the system.`
        : `Could not retrieve care gaps for patient "${patient}". ${err.response?.data?.detail || 'See console for details.'}`;
      store.dispatch(setError(errorMsg));
      return reject(err);
    });
  });
}

export default retrievePatient;
