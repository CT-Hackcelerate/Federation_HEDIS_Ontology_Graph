import * as types from './action-types';

/**
 * Sets the loading status of the application, used to display a loading spinner during network calls
 * @param {*} status - Boolean indicating whether or not the loader should be displayed
 */
export function setLoadingStatus(status) {
  return {
    type: types.SET_LOADING_STATUS,
    isLoaderOn: status,
  };
}

/**
 * Stores an error message to display to the user (empty string clears it)
 * @param {*} message - The error message to display
 */
export function setError(message) {
  return {
    type: types.SET_ERROR,
    message,
  };
}
