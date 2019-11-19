import { createStore, applyMiddleware } from "redux";
import reducer from "./reducers";
import properties from "./properties";
import monopolyMiddleware from "./middlewares";

const initialState = {
  players: [],
  currentPlayer: -1,
  myId: -1,
  currentPhase: "",
  playerAction: "",
  endpoints: {},
  rawState: {},
  bsmCandidates: {
    buyingCandidates: [],
    sellingCandidates: [],
    mortgageCandidates: []
  },
  properties,
  playersCash: {},
  playersPositions: {},
  formData: {},
  showPropertyModal: false,
  selectedPropertyIndex: -1,
  showJailDecisionModal: false,
  showToastMessage: false,
  toastMessage: "",
  toastTitle: ""
};

const middlewares = [];

//register our middleware
middlewares.push(monopolyMiddleware);

if (process.env.NODE_ENV === "development") {
  const { logger } = require("redux-logger");
  middlewares.push(logger);
}

const store = createStore(
  reducer,
  initialState,
  applyMiddleware(...middlewares)
);

export default store;
