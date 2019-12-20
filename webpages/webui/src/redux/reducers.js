import * as actionTypes from "./actionTypes";
import {
  adjustPlayerPositions,
  mergeProperties,
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates,
  getUnmortgageCandidates,
  getTradeCandidates } from "utils";

const reducer = (state, action) => {
  switch (action.type) {

    case actionTypes.SET_PROPS:
      const { props } = action;
      return {
        ...state,
        ...props
      };

    case actionTypes.SET_SELECTED_PROP_INDEX:
      const { selectedPropertyIndex } = action;

      if (state.phase === 'MORTGAGE') {
        if (state.mortgageCandidates.includes(selectedPropertyIndex) &&
          !state.actionProps.includes(selectedPropertyIndex)) {
          const mortValue = parseInt(state.properties[selectedPropertyIndex].price/2);
          return {
            ...state,
            selectedPropertyIndex,
            actionProps: [...state.actionProps, selectedPropertyIndex],
            actionCash: state.actionCash + mortValue
          };
        }
        return {
          ...state,
          selectedPropertyIndex
        };
      }
      if (state.phase === 'UNMORTGAGE') {
        if (state.unmortgageCandidates.includes(selectedPropertyIndex) &&
          !state.actionProps.includes(selectedPropertyIndex)) {
          const mortValue = parseInt(state.properties[selectedPropertyIndex].price/2);
          return {
            ...state,
            selectedPropertyIndex,
            actionProps: [...state.actionProps, selectedPropertyIndex],
            actionCash: state.actionCash - mortValue
          };
        }
        return {
          ...state,
          selectedPropertyIndex
        };
      }
      if (state.phase === 'TRADE') {
        if ((state.properties[selectedPropertyIndex].ownerId === state.myId) &&
          state.tradeCandidates.includes(selectedPropertyIndex) &&
          !state.actionProps.includes(selectedPropertyIndex)) {
          return {
            ...state,
            selectedPropertyIndex,
            actionProps: [...state.actionProps, selectedPropertyIndex]
          };
        }

        if ((state.properties[selectedPropertyIndex].ownerId === state.otherPlayerId) &&
          state.otherTradeCandidates.includes(selectedPropertyIndex) &&
          !state.otherActionProps.includes(selectedPropertyIndex)) {
          return {
            ...state,
            selectedPropertyIndex,
            otherActionProps: [...state.otherActionProps, selectedPropertyIndex]
          };
        }
      }
      return {
        ...state,
        selectedPropertyIndex
      };
    
    case actionTypes.SET_OTHER_PLAYER:
      const { otherPlayerId } = action;
      return {
        ...state,
        otherPlayerId,
        otherTradeCandidates: getTradeCandidates(state.properties,otherPlayerId)
      };

    case actionTypes.RECEIVE_MESSAGE:
      const { rawState } = action;
      const newProps = mergeProperties(state.properties, rawState.properties);
      return {
        ...state,
        players: rawState.player_ids,
        currentPlayer: rawState.current_player_id,
        turnNumber: rawState.turn_number,
        properties: newProps,
        playersPositions: adjustPlayerPositions(
          rawState.player_board_positions
        ),
        playersCash: rawState.player_cash,
        bankrupt: rawState.player_loss_status,
        phase: rawState.phase,
        phasePayload: rawState.phase_payload,
        timeout: rawState.timeout,
        selectedPropertyIndex: rawState.player_board_positions[state.myId],
        buyCandidates: getBuyingCandidates(newProps,state.myId),
        sellCandidates: getSellingCandidates(newProps,state.myId),
        mortgageCandidates: getMortgageCandidates(newProps,state.myId),
        unmortgageCandidates: getUnmortgageCandidates(newProps,state.myId),
        tradeCandidates: getTradeCandidates(newProps,state.myId)
      };

    case actionTypes.TOGGLE_PROPERTY_MODAL:
      const { showPropertyModal, propertyIndex } = action;
      return {
        ...state,
        showPropertyModal,
        propertyIndex
      };

    default:
      return state;
  }
};

export default reducer;
