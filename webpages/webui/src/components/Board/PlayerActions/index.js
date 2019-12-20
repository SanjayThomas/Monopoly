import React from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import JailDecision from "./JailDecision";
import BuyProperty from "./BuyProperty";
import Auction from "./Auction";
import BuyConstructions from "./BuyConstructions";
import SellConstructions from "./SellConstructions";
import Trade from "./Trade";
import TradeResponse from "./TradeResponse";
import Mortgage from "./Mortgage";
import Unmortgage from "./Unmortgage";
import DiceRoll from "./DiceRoll";
import { setProps } from "redux/actions";

const PlayerActions = ({ joined, phase, resUri, resetActionProps, resetTradeProps, setPhase }) => {

  const publish = args => {
    setPhase();
    setTimeout(() => {
      window.session.publish(resUri, [phase, ...args]);
    }, 1000);
  };

  let content = (<Card className="text-center">
                  <Card.Body>
                    <Card.Title>Waiting...</Card.Title>
                  </Card.Body>
                </Card>);

  switch(phase) {
    case 'WAITING':
    break;
    case 'PRE_GAME':
    content = (<Card className="text-center">
                <Card.Body>
                  <Card.Title>Join the game to Start</Card.Title>
                </Card.Body>
              </Card>);
    break;
    case 'JOINED':
    content = (<Card className="text-center">
                <Card.Body>
                  <Card.Title>Waiting for other players...</Card.Title>
                  You have successfully joined the game. Waiting for the other players to join.
                </Card.Body>
              </Card>);
    break;
    case 'JAIL':
    content = <JailDecision publish={publish}/>;
    break;
    case 'BUY':
    content = <BuyProperty publish={publish}/>;
    break;
    case 'BUY_HOUSES':
    resetActionProps();
    content = <BuyConstructions publish={publish}/>;
    break;
    case 'TRADE':
    resetTradeProps();
    content = <Trade publish={publish}/>;
    break;
    case 'TRADE_RESPONSE':
    content = <TradeResponse publish={publish}/>;
    break;
    case 'MORTGAGE':
    resetActionProps();
    content = <Mortgage publish={publish}/>;
    break;
    case 'UNMORTGAGE':
    resetActionProps();
    content = <Unmortgage publish={publish}/>;
    break;
    case 'SELL_HOUSES':
    resetActionProps();
    content = <SellConstructions publish={publish}/>;
    break;
    case 'AUCTION':
    content = <Auction publish={publish}/>;
    break;
    case 'DICE_ROLL':
    content = <DiceRoll publish={publish}/>;
    break;
    case 'START_GAME':
    content = (<Card className="text-center">
                <Card.Body>
                  <Card.Title>Game Started!</Card.Title>
                </Card.Body>
              </Card>);
    setTimeout(() => {
      window.session.publish(resUri,[phase]); 
    }, 3000);
    break;
    case 'END_GAME':
    content = (<Card className="text-center">
                <Card.Body>
                  <Card.Title>The game has ended</Card.Title>
                </Card.Body>
              </Card>);
    setTimeout(() => {
      window.session.publish(resUri,[phase]); 
    }, 1000);
    break;
    default:
    console.log("Calling "+resUri+" from PlayerActions default case.");
    setTimeout(() => {
      window.session.publish(resUri,[phase]); 
    }, 1000);
  }

  return (
    <div className="player-actions">
      {content}
    </div>
  );
};

const mapDispatchToProps = dispatch => ({
  resetActionProps: () =>
    dispatch(setProps({
      actionCash: 0,
      actionProps: []
    })),
  resetTradeProps: () =>
    dispatch(setProps({
      actionCash: 0,
      actionProps: [],
      otherPlayerId: "",
      otherActionProps: []
    })),
  setPhase: () => dispatch(setProps({
    phase: "WAITING"
  }))
});

const mapStateToProps = state => {
  return {
    joined: state.joined,
    phase: state.phase,
    resUri: state.resUri
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(PlayerActions);
