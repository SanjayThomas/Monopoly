import { createStore } from "redux";
import reducer from "./reducers";
import properties from "./properties";

const initialState = {
  joined: false,
  gameId: "",
  sessionId: "",
  myId: "",
  resUri: "",
  properties,
  players: [],
  currentPlayer: "",
  turnNumber: 0,
  playersPositions: {},
  playersCash: {},
  bankrupt: {},
  phase: "PRE_GAME",
  phasePayload: "",
  timeout: -1,
  selectedPropertyIndex: -1,
  propertyIndex: -1,

  actionCash: 0,
  actionProps: [],
  otherPlayerId: "",
  otherActionProps: [],

  buyCandidates: [],
  sellCandidates: [],
  mortgageCandidates: [],
  unmortgageCandidates: [],
  tradeCandidates: [],
  otherTradeCandidates: [],
  
  showPropertyModal: false
};

const store = createStore(
  reducer,
  initialState
);

export default store;
