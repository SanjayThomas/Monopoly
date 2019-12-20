import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";
import { convertTimer } from "utils";

class JailDecision extends Component {

  constructor(props, context) {
    super(props, context);

    const { myId, playersCash, properties, timeout, publish } = props;

    let disablePay = false;
    let currentPlayerCash = playersCash[myId];
    if (currentPlayerCash < 50) disablePay = true;

    let disableCards = true;
    let cardNo = 0;
    if (properties.length > 0) {
      if (properties[40].ownerId === myId) {
        cardNo = 40;
        disableCards = false;
      }
      else if(properties[41].ownerId === myId) {
        cardNo = 41;
        disableCards = false; 
      }
    }

    this.state = { disablePay: disablePay, disableCards: disableCards, cardNo: cardNo, timeout: timeout };
    
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
    const { turnNumber, publish } = this.props;
    const { disablePay, disableCards, cardNo, timeout } = this.state;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>How do you want to Get out of Jail?</Card.Title>
          <Button
            onClick={() => {
              publish(["R"]);
            }}
            variant="success"
            style={{ marginTop: "15px", marginBottom: "15px" }}
            block>
            Roll a Double
          </Button>
          <Button
            onClick={() => {
              publish(["P"]);
            }}
            variant="warning"
            disabled={disablePay}
            style={{ marginBottom: "15px" }}
            block>
            Pay $50
          </Button>
          <Button
            onClick={() => {
              publish([["C", cardNo]]);
            }}
            variant="info"
            disabled={disableCards}
            style={{ marginTop: "15px", marginBottom: "15px" }}
            block>
            Use Get Out of Jail Card
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
    playersCash: state.playersCash,
    timeout: state.timeout
  };
};

export default connect(
  mapStateToProps
)(JailDecision);
