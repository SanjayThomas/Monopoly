import React, { Component } from "react";
import { connect } from "react-redux";
import Autobahn from "autobahn";
import Board from "components/Board";
import UpdatesPanel from "components/UpdatesPanel";
import { substituteEndpoint } from "utils";
import {
  receieveMessage,
  setProps
} from "redux/actions";
import * as constants from "./constants";
import "./App.css";
import "bootstrap/dist/css/bootstrap.css";
import { setTimeout } from "timers";

class App extends Component {
  constructor(props, context) {
    super(props, context);
    window.session = null;
    this.subIds = [];
  }

  joinGame = async () => {
    const { setJoined, gameId, sessionId } = this.props;

    const joinGameUri = substituteEndpoint(
      constants.JOIN_GAME_ENDPOINT,
      null,
      gameId
    );
    var agentOptions = {
      START_TURN: true,
      DICE_ROLL: true,
      CHANCE_CARD: true,
      COMMUNITY_CHEST: true,
      END_TURN: true
    };

    const response = await window.session.call(joinGameUri, [sessionId, agentOptions]);
    if (response[0] === 1) {
      alert(response[1]);
      return;
    }
    const myId = response[1];

    const reqUri = substituteEndpoint(
      constants.REQ_ENDPOINT,
      sessionId,
      gameId
    );
    const resUri = substituteEndpoint(
      constants.RES_ENDPOINT,
      sessionId,
      gameId
    );

    window.session.subscribe(reqUri, this.mapper);
    setJoined(myId,resUri);
  };

  componentDidMount() {
    const url = constants.ROUTER_ENDPOINT;
    const realm = constants.APPLICATION_REALM;

    // the variable name is important here
    const connection = new Autobahn.Connection({url, realm});

    connection.onopen = session => {
      window.session = session;
    };

    connection.open();
  }

  mapper = state => {
    const { resUri, receieveMessage } = this.props;

    state = JSON.parse(state);
    console.log("Entering the phase: "+state.phase);

    // the JSON from the PubSub call is populated into the redux global state.
    // this state is processed in PlayerActions
    receieveMessage(state);
    
  };

  render() {
    const { setGameAndSession } = this.props;
    const { joinGame } = this;
    return (
      <div className="App">
        <Board/>
        <UpdatesPanel setGameAndSession={setGameAndSession} joinGame={joinGame}/>
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  receieveMessage: (rawState) =>
    dispatch(receieveMessage(rawState)),
  setJoined: (myId, resUri) => dispatch(setProps({
    phase: 'JOINED',
    myId: myId,
    resUri: resUri
  })),
  setGameAndSession: (gameId,sessionId) => dispatch(setProps({
    gameId: gameId,
    sessionId: sessionId
  }))
});

const mapStateToProps = state => {
  return {
    sessionId: state.sessionId,
    gameId: state.gameId,
    myId: state.myId,
    resUri: state.resUri
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(App);
