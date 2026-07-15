import * as types from '../actions/action-types';

const initialState = {
  isLoadingData: false,
  errorMessage: '',
};

const uiReducers = (state = initialState, action) => {
  switch (action.type) {
    // Toggle the loading spinner during network calls
    case types.SET_LOADING_STATUS: {
      return { ...state, isLoadingData: action.isLoaderOn };
    }
    // Store (or clear) an error message shown to the user
    case types.SET_ERROR: {
      return { ...state, errorMessage: action.message };
    }
    default:
      return state;
  }
};

export default uiReducers;
