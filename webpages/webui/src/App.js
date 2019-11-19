import React, { Component } from "react";
import { connect } from "react-redux";
import Autobahn from "autobahn";
import Board from "components/Board";
import JailDecision from "components/JailDecision";
import ToastMessage from "components/ToastMessage";
import Button from "react-bootstrap/Button";
import { substituteEndpoint, calculateRent } from "utils";
import {
  receieveMessage,
  setMyId,
  setEndpoints,
  togglePropertyModal,
  toggleJailDecisionModal,
  toggleToastMessageModal
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
    this.state = {
      showStartButton: true
    };
  }

  startGame = async () => {
    const res = await window.session.call("com.monopoly.init_game", [2, 1, 1]);
    await window.session.call("com.monopoly.add_our_agent", [res.gameId]);
    const joinGameUri = substituteEndpoint(
      constants.JOIN_GAME_ENDPOINT,
      null,
      res.gameId
    );
    var agentOptions = {
      START_TURN: true,
      END_TURN: true,
      DICE_ROLL: true,
      PREMPTIVE_BSM: true
    };
    const response = await window.session.call(joinGameUri, [agentOptions]);
    const { setMyId, setEndpoints } = this.props;
    const myId = response["agent_id"];
    setMyId(myId);
    delete response["agent_id"];
    setEndpoints(response);
    this.subscribeToEvents(response);
    await window.session.call(response["CONFIRM_REGISTER"]);
  };

  //deprecated
  componentWillMount() {
    const url = constants.ROUTER_ENDPOINT;
    const realm = constants.APPLICATION_REALM;

    const connection = new Autobahn.Connection({
      url,
      realm
    });

    connection.onopen = session => {
      window.session = session;
    };

    connection.open();
  }

  /* Receivers  */
  receiveRequest = (phase, state) => {
    const { receieveMessage } = this.props;
    state = JSON.parse(state);
    receieveMessage(state, phase);
  };

  subscribeToEvents = response => {
    //not implementing trade for the time being; just rejecting all trade responses
    window.session
      .subscribe(response["RESPOND_TRADE_IN"], state => {
        window.session.publish(response["RESPOND_TRADE_OUT"], [false]);
      })
      .then(subId => {
        this.subIds.push(subId);
      });
    window.session
      .subscribe(response["TRADE_IN"], state => {
        window.session.publish(response["TRADE_OUT"], [false]);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //start game
    window.session
      .subscribe(response["START_GAME_IN"], state => {
        this.receiveRequest.bind(this, "start_game");
        window.session.publish(response["START_GAME_OUT"], []);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    window.session
      .subscribe(
        response["START_TURN_IN"],
        this.receiveRequest.bind(this, "start_turn")
      )
      .then(subId => {
        this.subIds.push(subId);
      });

    window.session
      .subscribe(response["END_TURN_IN"], state => {
        window.session.publish(response["END_TURN_OUT"]);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //how do you want to get out jail?
    window.session
      .subscribe(response["JAIL_IN"], state => {
        const { toggleJailDecisionModal, receieveMessage } = this.props;
        state = JSON.parse(state);
        receieveMessage(state, "jail_decision");
        toggleJailDecisionModal(true);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //generic receive state
    window.session
      .subscribe(response["BROADCAST_IN"], state => {
        const { receieveMessage, toggleToastMessageModal, myId } = this.props;
        state = JSON.parse(state);
        let phase = constants.PhaseNameMapping[state.current_phase_number];
        const currentPlayer = state.current_player_id;
        const phasePayload = state.phase_payload;
        let message = "",
          title = "",
          currentPlayerName = "",
          opponentPlayerName = "";

        if (myId === currentPlayer) {
          currentPlayerName = "Human";
          opponentPlayerName = "Robot";
        } else {
          currentPlayerName = "Robot";
          opponentPlayerName = "Human";
        }

        if (phase === "chance_card") {
          title = "Chance Card";
          message = `${currentPlayerName} won a Chance Card - ${
            constants.chanceCards[phasePayload].content
          }`;
        }

        if (phase === "community_chest_card") {
          title = "Community Chest Card";
          message = `${currentPlayerName} won a Community Chest Card - ${
            constants.communityChestCards[phasePayload].content
          }`;
        }

        if (phase === "payment") {
          title = "Rent";
          const rent = calculateRent(state.player_debts, currentPlayer);
          message = `Player ${currentPlayerName} landed on ${opponentPlayerName}'s property. 
        ${currentPlayerName} pays ${opponentPlayerName} - ${rent}`;
        }

        if (message && message.length) {
          setTimeout(() => {
            receieveMessage(state, phase);
            toggleToastMessageModal(false);
            window.session.publish(response["BROADCAST_OUT"], []);
          }, 4000);
          toggleToastMessageModal(true, title, message);
        } else {
          receieveMessage(state, phase);
          window.session.publish(response["BROADCAST_OUT"], []);
        }
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //auction property
    window.session
      .subscribe(response["AUCTION_IN"], state => {
        const { togglePropertyModal, receieveMessage } = this.props;
        state = JSON.parse(state);
        const propertyToAuction = state.phase_payload;
        receieveMessage(state, "auction_property");
        togglePropertyModal(true, propertyToAuction);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //buy property
    window.session
      .subscribe(response["BUY_IN"], state => {
        const { receieveMessage, togglePropertyModal } = this.props;
        state = JSON.parse(state);
        const propertyToBuy = parseInt(state.phase_payload);
        receieveMessage(state, "buy_property");
        togglePropertyModal(true, propertyToBuy);
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //conduct a BSM
    window.session
      .subscribe(response["BSM_IN"], state => {
        state = JSON.parse(state);
        const { receieveMessage } = this.props;
        receieveMessage(state, "bsm");
      })
      .then(subId => {
        this.subIds.push(subId);
      });

    //end game
    window.session
      .subscribe(response["END_GAME_IN"], state => {
        const { myId, toggleToastMessageModal } = this.props;
        var unsub = false;

        const result = state[0] || {};

        if (result) {
          if (typeof result === "string") {
            let winMessage = "lost";

            if (myId in result) {
              winMessage = "won";
            }
            toggleToastMessageModal(
              true,
              "Game Ended",
              `You ${winMessage} this game.`
            );
          } else {
            //This is the final winCount message. Start teardown.
            //toggleToastMessageModal(true, "Game Ended", `All the games have ended.`);
            unsub = true;
          }
        }

        window.session.publish(response["END_GAME_OUT"], []);
        if (unsub) {
          for (var subId in this.subIds) {
            subId.unsubscribe();
          }
        }
      })
      .then(subId => {
        this.subIds.push(subId);
      });
  };

  render() {
    const { showStartButton } = this.state;
    const { startGame } = this;
    return (
      <div className="App">
        <Board />
        {showStartButton && (
          <Button
            onClick={startGame}
            style={{ marginTop: "40px" }}
            size="lg"
            variant="success"
          >
            Start Game
          </Button>
        )}
        <JailDecision />
        <ToastMessage />
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  receieveMessage: (rawState, phase) =>
    dispatch(receieveMessage(rawState, phase)),
  setMyId: id => dispatch(setMyId(id)),
  setEndpoints: endpoints => dispatch(setEndpoints(endpoints)),
  togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
    dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex)),
  toggleJailDecisionModal: showJailDecisionModal =>
    dispatch(toggleJailDecisionModal(showJailDecisionModal)),
  toggleToastMessageModal: (showToastMessage, toastTitle, toastMessage) =>
    dispatch(
      toggleToastMessageModal(showToastMessage, toastTitle, toastMessage)
    )
});

const mapStateToProps = state => {
  return {
    myId: state.myId
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(App);
