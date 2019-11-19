import { createStore } from "redux";
import reducer from "./reducers";
import { PAGE_TYPES } from '../components/constants';

const initialState = {
  pageType: PAGE_TYPES.create_solo,
  currentGameId: -1,
  sessionId: null,
  email: null
};

const store = createStore(
  reducer,
  initialState
);

export default store;
