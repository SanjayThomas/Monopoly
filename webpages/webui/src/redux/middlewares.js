import * as actionTypes from "./actionTypes";
import { setBSMCandidates, resetForm } from "./actions";
import {
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates
} from "utils";

const middleware = store => next => async action => {
  const dispatch = store.dispatch;
  let state = store.getState();
  const { endpoints } = state;
  const endpoint = endpoints.BSM_OUT;

  if (action.type === actionTypes.RECEIVE_MESSAGE && action.phase === "bsm") {
    next(action);
    state = store.getState();

    const buyingCandidates = getBuyingCandidates(state);
    const sellingCandidates = getSellingCandidates(state);
    const mortgageCandidates = getMortgageCandidates(state);

    if (
      buyingCandidates.length === 0 &&
      sellingCandidates.length === 0 &&
      mortgageCandidates.length === 0
    ) {
      window.session.publish(endpoint, []);
    }
    dispatch(
      setBSMCandidates({
        buyingCandidates,
        sellingCandidates,
        mortgageCandidates
      })
    );

    return;
  }

  // finally send to adjudicator
  else if (action.type === actionTypes.PUBLISH_ACTION) {
    const { formData, playerAction } = state;
    const payload = [];

    if (formData === null || Object.keys(formData).length === 0) {
      window.session.publish(endpoint, []);
      dispatch(resetForm());
      return;
    }

    if (playerAction === "buy-constructions") {
      payload[0] = "BHS";
      payload[1] = Object.keys(formData).map(key => [
        key,
        formData[key]["housesBought"]
      ]);
    } else if (playerAction === "sell-constructions") {
      payload[0] = "S";
      payload[1] = Object.keys(formData).map(key => [
        key,
        formData[key]["housesSold"]
      ]);
    } else if (playerAction === "mortage-unmortgage") {
      payload[0] = "M";
      payload[1] = Object.keys(formData).filter(
        key => formData[key]["mortgaged"]
      );
    }
    window.session.publish(endpoint, [payload]);
    dispatch(resetForm());
  }

  next(action);
};

export default middleware;
