import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { convertTimer } from "utils";

class Auction extends Component {

  constructor(props, context) {
    super(props, context);

    const { publish } = props;

    this.state = {
      timeout: props.timeout,
      bid: 0
    };
    
    this.timerID = setInterval(
    () => {
      this.setState((state, props) => ({
        timeout: state.timeout - 1 > 0 ? state.timeout - 1 : 0
      }));

      if (this.state.timeout === 0) {
        clearInterval(this.timerID);
        console.log("Timer expired!");
        publish([]);
      }
    },1000);
  }

  componentWillUnmount() {
    // preventing state update after leaving component
    if (this.timerID) clearInterval(this.timerID);
  }
  
  render() {
    const { myId, turnNumber, properties, phasePayload, playersCash, publish } = this.props;
    const { timeout, bid } = this.state;
    const { name } = properties[phasePayload];

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Auction for property {name} (#{phasePayload}).</Card.Title>
          <Form.Control
              min={0}
              max={playersCash[myId]}
              placeholder="Bid Amount"
              aria-label="Bid Amount"
              type="number"
              value={bid}
              className="cst-ig"
              onChange={event => this.setState({bid: parseInt(event.target.value)})}
            />
          <Button variant="primary" className="mt-3 cst-btn" type="button" onClick={ () => {
            if (bid > playersCash[myId] || bid < 0) alert("Invalid Bid Amount");
            else publish([bid]);
          }}>
            Submit
          </Button>
        </Card.Body>
        <Card.Footer>Time Remaining: <strong>{convertTimer(timeout)}</strong></Card.Footer>
      </Card>
    );
  }
}
const mapStateToProps = state => {
  return {
    myId: state.myId,
    turnNumber: state.turnNumber,
    properties: state.properties,
    phase: state.phase,
    phasePayload: state.phasePayload,
    timeout: state.timeout,
    playersCash: state.playersCash
  };
};

export default connect(
  mapStateToProps
)(Auction);