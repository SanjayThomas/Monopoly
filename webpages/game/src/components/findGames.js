import React, { useState } from "react";
import { connect } from "react-redux";
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Button from "react-bootstrap/Button";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import GameDetails from './gameDetails.js';

const FindGames = props => {
  const [gameId, setGameId] = useState("");
  const [renderDetail, setRenderDetail] = useState(false);

  return (
  <Row>
    <Col md={2}></Col>
    <Col md={8}>
    <InputGroup className="mb-5">
      <FormControl
      placeholder="Enter the Game ID"
      aria-label="Enter the Game ID"
      value={gameId}
      onChange={event => setGameId(event.target.value)}/>
      <InputGroup.Append>
        <Button variant="outline-secondary" onClick={() => {
          setRenderDetail(true);
        }}>Search</Button>
      </InputGroup.Append>
    </InputGroup>
    {renderDetail ? <GameDetails key={gameId.split(" ")[0]} currentGameId={gameId.split(" ")[0]}/> : ""}
    </Col>
    <Col md={2}></Col>
  </Row>
  );
};

const mapDispatchToProps = dispatch => ({});

const mapStateToProps = state => {
  return {
    sessionId: state.sessionId
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FindGames);