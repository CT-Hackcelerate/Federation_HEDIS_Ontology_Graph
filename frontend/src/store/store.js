import { createStore } from 'redux';
import reducers from '../reducers/index';

// The POC has no async/side-effecting middleware (network calls dispatch plain actions directly),
// so a plain Redux store is all that's needed.
const store = createStore(reducers);

export default store;
