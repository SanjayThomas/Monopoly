import * as actionTypes from "./actionTypes";

export const setProps = props => {
  return { type: actionTypes.SET_PROPS, props };
};