import React, { useState } from "react";
import { connect } from "react-redux";
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from "react-bootstrap/Button";
import Toast from 'react-bootstrap/Toast';

import { setProps } from "../redux/actions.js";

import { PAGE_TYPES, ONE_OFF, GAME_TYPE_TEXT, createEndpoint } from './constants';

const CreateGame = props => {
  const [noPlayers, setNoPlayers] = useState(2);
  const [noGames, setNoGames] = useState(100);
  const [noPpg, setNoPpg] = useState(2);
  const [allowHuman, setAllowHuman] = useState(false);
  const [timePerMove, setTimePerMove] = useState(5);

  // By default, assume the game is a One-Off game
  let gameType = ONE_OFF;

  if ('type' in props) { gameType = props.type; }

  return (
    <Row>
    <Col md={4}></Col>
    <Col md={4}>
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
          disabled={allowHuman}
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
      <Form.Group controlId="formGroupTime">
        <Form.Label>Time per Move (in seconds)</Form.Label>
        <Form.Control
          type="number"
          placeholder="Time per Move"
          min="3"
          value={timePerMove}
          onChange={event => setTimePerMove(event.target.value)} />
      </Form.Group>
      {gameType === ONE_OFF && <Form.Check custom
        type='checkbox'
        id='allow_human'
        label='Allow Human Players?'
        checked={allowHuman}
        onChange={
          event => {
            setNoGames(1);
            setTimePerMove(60);
            setAllowHuman(event.target.checked);
          }
        }
        style={{ marginBottom: '1rem' }}/>}
      <Button variant="primary" onClick={() => {
        if (window.session === undefined) {
          console.log("The session hasn't been initialized yet.")
          return;
        }
        const data = gameType === ONE_OFF ? [props.sessionId, gameType, noPlayers, noGames, timePerMove, allowHuman]
         : [props.sessionId, gameType, noPlayers, noGames, timePerMove, allowHuman, noPpg];
        window.session.call(createEndpoint, data).then(
        data => {
          if (data[0] === 1) {
            alert(data[1]);
          }
          else {
            props.showDetail(data[1]);
          }
        });
      }}>Start Game</Button>
    </Form>
    </Col>
    <Col md={4}>
      <div
      style={{
        position: 'absolute',
        top: 0,
        right: '4%',
      }}>
      <Toast show={true}>
        <Toast.Header closeButton={false}>
          <div className="toast_tag"/>
          <p className="toast_text">No of Players</p>
        </Toast.Header>
        <Toast.Body>Total number of players (agents or humans) who are going to play in this game. Can range from 2-8.</Toast.Body>
      </Toast>
      <Toast show={true}>
        <Toast.Header closeButton={false}>
          <div className="toast_tag"/>
          <p className="toast_text">No of Games</p>
        </Toast.Header>
        <Toast.Body>When you start a game, you are infact starting a sequence of games between the agents.
        After the whole sequence is done, the result of all the games are published to all the agents and here.</Toast.Body>
      </Toast>
      <Toast show={true}>
        <Toast.Header closeButton={false}>
          <div className="toast_tag"/>
          <p className="toast_text">Time per Move (in seconds)</p>
        </Toast.Header>
        <Toast.Body>Time allowed for an agent in this game to make their move.
        If the agent doesn't respond in this time, a default action is taken and the game progresses.</Toast.Body>
      </Toast>
      <Toast show={true}>
        <Toast.Header closeButton={false}>
          <div className="toast_tag"/>
          <p className="toast_text">Allow Human Players</p>
        </Toast.Header>
        <Toast.Body>Both Human Players and AI agents can take part in these games.</Toast.Body>
      </Toast>
    </div>
    </Col>
    </Row>
  );
};

const mapDispatchToProps = dispatch => ({
  showDetail: currentGameId => dispatch(setProps({
    currentGameId: currentGameId,
    pageType: PAGE_TYPES.game_details
  }))
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