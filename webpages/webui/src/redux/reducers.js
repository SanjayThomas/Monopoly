import * as actionTypes from "./actionTypes";
import { adjustPlayerPositions, mergeProperties } from "utils";

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.RECEIVE_MESSAGE:
      const { rawState, phase } = action;
      return {
        ...state,
        ...rawState,
        phase,
        properties: mergeProperties(state.properties, rawState.properties),
        players: rawState.player_ids,
        currentPlayer: rawState.current_player_id,
        playersPositions: adjustPlayerPositions(
          rawState.player_board_positions
        ),
        playersCash: rawState.player_cash
      };

    case actionTypes.SET_MY_ID:
      const { id: myId } = action;
      return {
        ...state,
        myId: myId
      };

    case actionTypes.SET_ENDPOINTS:
      const { endpoints } = action;
      return {
        ...state,
        endpoints: endpoints
      };

    case actionTypes.SET_PLAYER_ACTION:
      const { playerAction } = action;
      return {
        ...state,
        playerAction
      };

    case actionTypes.SET_BSM_CANDIDATES:
      const { bsmCandidates } = action;
      return {
        ...state,
        bsmCandidates
      };

    case actionTypes.SET_FORM_DATA:
      const { formData, propertyId } = action;
      return {
        ...state,
        formData: {
          ...state.formData,
          [propertyId]: formData
        }
      };

    case actionTypes.RESET_FORM:
      return {
        ...state,
        formData: {},
        playerAction: ""
      };

    case actionTypes.TOGGLE_PROPERTY_MODAL:
      const { showPropertyModal, selectedPropertyIndex } = action;
      return {
        ...state,
        showPropertyModal,
        selectedPropertyIndex
      };

    case actionTypes.TOGGLE_JAIL_DECISION_MODAL:
      const { showJailDecisionModal } = action;
      return {
        ...state,
        showJailDecisionModal
      };

    case actionTypes.TOGGLE_TOAST_MESSAGE:
      const { showToastMessage, toastTitle, toastMessage } = action;
      return {
        ...state,
        showToastMessage,
        toastTitle,
        toastMessage
      };

    default:
      return state;
  }
};

export default reducer;
