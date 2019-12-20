import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from "react-bootstrap/Button";
import { convertTimer } from "utils";

class TradeResponse extends Component {

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
    const { turnNumber, properties, phasePayload, publish } = this.props;
    const { timeout } = this.state;
    const [otherPlayer, cashOffer, propsOffer, cashReceive, propsReceive] = phasePayload;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Trade request from {otherPlayer}</Card.Title>
          <Row>
            <Col sm="6" className="border-right">
              <h5>Offer</h5>
            </Col>
            <Col sm="6">
              <h5>Request</h5>
            </Col>
          </Row>
          <Row>
            <Col sm="6" className="p-sm-0 border-right">
              {propsOffer.length > 0 && propsOffer.map((construct,i) => {
                var initials = properties[construct].name.match(/\b\w/g) || [];
                initials = ((initials.shift() || '') + (initials.pop() || ''));
                return (<Button key={i} size="sm" style={{ paddingLeft: '2px', paddingRight: '2px' }}
                        className={`construct-group pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}>
                          {initials} ${properties[construct].price}
                        </Button>);
              })
              }
            </Col>
            <Col sm="6" className="p-sm-0">
              {propsReceive.map((construct,i) => {
                var initials = properties[construct].name.match(/\b\w/g) || [];
                initials = ((initials.shift() || '') + (initials.pop() || ''));
                return (<Button  key={i} size="sm" style={{ paddingLeft: '2px', paddingRight: '2px' }} 
                        className={`construct-group pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}>
                          {initials} ${properties[construct].price}
                        </Button>);
              })
              }
            </Col>
          </Row>
          <Row>
            <Col sm="6" className="border-right">
              <h6>Cash: ${cashOffer}</h6>
            </Col>
            <Col sm="6">
              <h6>Cash: ${cashReceive}</h6>
            </Col>
          </Row>
          <div>
          <Button size="sm" variant="outline-success" style={{marginRight:'2em'}} type="button" onClick={() => {
            publish([true]);
          }}>
            Accept
          </Button>
          <Button size="sm" variant="outline-danger" type="button" onClick={() => {
            publish([false]);
          }}>
            Reject
          </Button>
          </div>
        </Card.Body>
        <Card.Footer>Time Remaining: <strong>{convertTimer(timeout)}</strong></Card.Footer>
      </Card>
    );
  }
}
const mapStateToProps = state => {
  return {
    turnNumber: state.turnNumber,
    properties: state.properties,
    phasePayload: state.phasePayload,
    timeout: state.timeout
  };
};

export default connect(
  mapStateToProps
)(TradeResponse);