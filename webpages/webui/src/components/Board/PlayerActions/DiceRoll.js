import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";
import { convertTimer } from "utils";

class DiceRoll extends Component {

  constructor(props, context) {
    super(props, context);

    const { publish } = props;

    this.state = {
      timeout: props.timeout
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
    const { myId, turnNumber, properties, playersPositions, phasePayload, publish } = this.props;
    const { timeout } = this.state;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Dice Roll</Card.Title>
          <h6>You rolled a {phasePayload[0]} and a {phasePayload[1]} and landed in {properties[playersPositions[myId]].name}(#{playersPositions[myId]}).</h6>
          <p>Note: No user action is required here. Simply press 'Done' when you are ready.</p>
          <Button variant="primary" className="cst-btn" type="button" onClick={() => {
              publish([]);
            }}>
              Done
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
    phasePayload: state.phasePayload,
    playersPositions: state.playersPositions,
    timeout: state.timeout
  };
};

export default connect(
  mapStateToProps
)(DiceRoll);