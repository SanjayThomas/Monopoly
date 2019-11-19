import * as actionTypes from "./actionTypes";

export const setProp = (prop,value) => {
  return { type: actionTypes.SET_PROP, prop, value };
};