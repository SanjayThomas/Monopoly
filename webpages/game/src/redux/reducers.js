import * as actionTypes from "./actionTypes";

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_PROP:
      const { prop, value } = action;
      return {
        ...state,
        [prop]: value 
      };

    default:
      return state;
  }
};

export default reducer;
