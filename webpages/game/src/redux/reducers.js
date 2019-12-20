import * as actionTypes from "./actionTypes";

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_PROPS:
      const { props } = action;
      return {
        ...state,
        ...props
      };

    default:
      return state;
  }
};

export default reducer;
