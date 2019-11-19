import React, { useState } from "react";
import { connect } from "react-redux";
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from "react-bootstrap/Button";

import { setProp } from "../redux/actions.js";

import { PAGE_TYPES, ONE_OFF, GAME_TYPE_TEXT, createEndpoint } from './constants';

const CreateGame = props => {
  const [noPlayers, setNoPlayers] = useState(2);
  const [noGames, setNoGames] = useState(100);
  const [noPpg, setNoPpg] = useState(2);
  const [privateGame, setPrivateGame] = useState(false);

  // By default, assume the game is a One-Off game
  let gameType = ONE_OFF;

  if ('type' in props) { gameType = props.type; }

  return (
    <Row>
    <Col md={3}></Col>
    <Col md={6}>
    <h2 style={{ textDecoration: 'underline', marginBottom: '40px' }}> Create a {GAME_TYPE_TEXT[gameType]}</h2>

    <Form>
      <Form.Group controlId="formGroupPlayers">
        <Form.Label>Number of Players</Form.Label>
        <Form.Control
          type="number"
          placeholder="Number of Players"
          min="2"
          max="{ gameType === ONE_OFF ? 8 : '' }"
          value={noPlayers}
          onChange={event => setNoPlayers(event.target.value)} />
      </Form.Group>
      <Form.Group controlId="formGroupGames">
        <Form.Label>Number of Games</Form.Label>
        <Form.Control
          type="number"
          placeholder="Number of Games"
          min="1"
          value={noGames}
          onChange={event => setNoGames(event.target.value)} />
      </Form.Group>
      {gameType !== ONE_OFF && 
      <Form.Group controlId="formGroupPpG">
        <Form.Label>Number of Players per Game</Form.Label>
        <Form.Control
          type="number"
          placeholder="Between 2 and 8 players"
          min="2" max="8"
          value={noPpg}
          onChange={event => setNoPpg(event.target.value)}/>
      </Form.Group>}
      {false && 
        <Form.Check custom
        type='checkbox'
        id='private_checkbox'
        label='Private Game'
        value={privateGame}
        onChange={event => setPrivateGame(event.target.value)}
        style={{ marginBottom: '1rem' }}/>
      }
      <Button variant="primary" onClick={() => {
        if (window.session === undefined) {
          console.log("The session hasn't been initialized yet.")
          return;
        }
        const data = gameType === ONE_OFF ? [props.sessionId, gameType, noPlayers, noGames] : [props.sessionId, gameType, noPlayers, noGames, noPpg];
        window.session.call(createEndpoint, data).then(
        gameId => {
          if (gameId === "ERROR") {
            console.log("Error while creating the game.");
          }
          else {
            props.setCurrentGameId(gameId);
            props.setPageType(PAGE_TYPES.game_details);
          }
        });
      }}>Start Game</Button>
    </Form>
    </Col>
    <Col md={3}></Col>
    </Row>
  );
};

const mapDispatchToProps = dispatch => ({
  setPageType: pageType =>
    dispatch(setProp("pageType", pageType)),
  setCurrentGameId: currentGameId =>
    dispatch(setProp("currentGameId", currentGameId))
});

const mapStateToProps = state => {
  return {
    pageType: state.pageType,
    currentGameId: state.currentGameId,
    sessionId: state.sessionId
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateGame);