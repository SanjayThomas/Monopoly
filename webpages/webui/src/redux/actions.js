import * as actionTypes from "./actionTypes";

export const receieveMessage = rawState => {
  return { type: actionTypes.RECEIVE_MESSAGE, rawState };
};

export const setProps = props => {
  return { type: actionTypes.SET_PROPS, props };
};

export const setSelectedPropIndex = selectedPropertyIndex => {
  return { type: actionTypes.SET_SELECTED_PROP_INDEX, selectedPropertyIndex };
};

export const setOtherPlayerId = otherPlayerId => {
  return { type: actionTypes.SET_OTHER_PLAYER, otherPlayerId };
};

export const togglePropertyModal = (
  showPropertyModal,
  selectedPropertyIndex
) => {
  return {
    type: actionTypes.TOGGLE_PROPERTY_MODAL,
    showPropertyModal,
    selectedPropertyIndex
  };
};
