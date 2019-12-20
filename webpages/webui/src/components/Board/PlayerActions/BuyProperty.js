import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Form from "react-bootstrap/Form";
import { convertTimer } from "utils";

class BuyProperty extends Component {

  constructor(props, context) {
    super(props, context);

    const { publish } = props;

    this.state = { timeout: props.timeout };
    
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
    const { turnNumber, properties, phasePayload, publish } = this.props;
    const { timeout } = this.state;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Do you want to buy {properties[phasePayload].name} for ${properties[phasePayload].price}?</Card.Title>
          <Form.Check
            onChange={event => {
              publish([true]);
            }}
            type="radio"
            label="Yes"
          />
          <Form.Check
            onChange={event => {
              publish([false]);
            }}
            type="radio"
            label="No"
          />
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
    timeout: state.timeout
  };
};

export default connect(
  mapStateToProps
)(BuyProperty);