import React from "react";
import { connect } from "react-redux";
import Button from "react-bootstrap/Button";
import { setPlayerAction, publishAction } from "redux/actions";

const PlayerActions = ({
  phase,
  startTurnEndpoint,
  setPlayerAction,
  publishAction,
  bsmCandidates
}) => {
  const {
    buyingCandidates,
    sellingCandidates,
    mortgageCandidates
  } = bsmCandidates;

  const activateBuy = buyingCandidates.length;
  const activateSell = sellingCandidates.length;
  const activateMortgage = mortgageCandidates.length;

  const click = playerAction => {
    setPlayerAction(playerAction);
  };

  return (
    <div className="player-actions">
      <h2 className="label">Player Actions</h2>
      {phase === "bsm" && (
        <div>
          <Button
            onClick={click.bind(null, "buy-constructions")}
            variant="secondary"
            {...{ disabled: !activateBuy }}
          >
            Buy Constructions
          </Button>
          <Button
            onClick={click.bind(null, "sell-constructions")}
            variant="success"
            {...{ disabled: !activateSell }}
          >
            Sell Constructions
          </Button>
          <Button
            onClick={click.bind(null, "mortage-unmortgage")}
            variant="warning"
            {...{ disabled: !activateMortgage }}
          >
            Mortgage/Unmortgage
          </Button>
          {(activateBuy || activateSell || activateMortgage) && (
            <Button
              onClick={() => {
                publishAction();
              }}
              variant="danger"
              size="lg"
            >
              Finish BSM
            </Button>
          )}
        </div>
      )}

      {phase === "start_turn" && (
        <Button
          onClick={() => {
            window.session.publish(startTurnEndpoint);
          }}
          variant="secondary"
        >
          Start Turn
        </Button>
      )}
    </div>
  );
};

const mapDispatchToProps = dispatch => {
  return {
    setPlayerAction: playerAction => dispatch(setPlayerAction(playerAction)),
    publishAction: () => dispatch(publishAction())
  };
};

const mapStateToProps = state => {
  return {
    startTurnEndpoint: state.endpoints.START_TURN_OUT,
    bsmCandidates: state.bsmCandidates
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(PlayerActions);
