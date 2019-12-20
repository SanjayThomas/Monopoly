import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Form from "react-bootstrap/Form";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Dropdown from 'react-bootstrap/Dropdown';
import Button from "react-bootstrap/Button";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { convertTimer } from "utils";
import {
  setProps,
  setOtherPlayerId
} from "redux/actions";

class Trade extends Component {

  constructor(props, context) {
    super(props, context);

    const { players, myId, setOtherPlayerId, publish } = props;

    for (let player of players) {
      if (player !== myId) {
        setOtherPlayerId(player);
        break;
      }
    }

    this.state = {
      cashOffer: 0,
      cashReceive: 0,
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
    const { myId, players, playersCash, turnNumber, properties, actionProps,
      setActionProps, otherActionProps, setOtherActionProps, otherPlayerId,
      setOtherPlayerId, publish } = this.props;
    const { cashOffer, cashReceive, timeout } = this.state;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Trade with&nbsp;
            <DropdownButton
              size="sm"
              title={otherPlayerId}
              variant="outline-primary"
              style={{display:'inline'}}
              onSelect={eventKey => setOtherPlayerId(eventKey)}>
              {players.map((player,i) => {
                if (player !== myId) {
                  return <Dropdown.Item key={i} eventKey={player}>{player}</Dropdown.Item>;  
                }
              })}
            </DropdownButton>
            &nbsp;?
          </Card.Title>
          <Row>
            <Col sm="6">
              <h5>Offer</h5>
            </Col>
            <Col sm="6">
              <h5>Request</h5>
            </Col>
          </Row>
          <Row>
            <Col sm="6" className="p-sm-0">
              {actionProps.length === 0 && <p>Select properties you own from the board to offer them in the trade.</p>}
              {actionProps.map((construct,i) => {
                var initials = properties[construct].name.match(/\b\w/g) || [];
                initials = ((initials.shift() || '') + (initials.pop() || ''));
                return (<ButtonGroup key={i} size="sm" className="construct-group">
                          <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                          style={{ paddingRight: '2px' }}>
                            {initials} ${properties[construct].price}
                          </Button>
                          <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                          onClick={() => setActionProps(actionProps.filter((fv,fi) => fi!==i))}>
                            <FontAwesomeIcon icon={faTimes} />
                          </Button>
                        </ButtonGroup>);
              })
              }
            </Col>
            <Col sm="6" className="p-sm-0">
              {otherActionProps.length === 0 && <p>Select properties owned by {otherPlayerId} to request them in the trade.</p>}
              {otherActionProps.map((construct,i) => {
                var initials = properties[construct].name.match(/\b\w/g) || [];
                initials = ((initials.shift() || '') + (initials.pop() || ''));
                return (<ButtonGroup key={i} size="sm" className="construct-group">
                          <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                          style={{ paddingRight: '2px' }}>
                            {initials} ${properties[construct].price}
                          </Button>
                          <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                          onClick={() => setOtherActionProps(otherActionProps.filter((fv,fi) => fi!==i))}>
                            <FontAwesomeIcon icon={faTimes} />
                          </Button>
                        </ButtonGroup>);
              })
              }
            </Col>
          </Row>
          <Row>
            <Col sm="6">
              <Form.Control
                size="sm"
                className="cst-ig mt-1 mb-3"
                min={0}
                max={playersCash[myId]}
                placeholder="Cash Offer"
                aria-label="Cash Offer"
                type="number"
                onChange={event => this.setState({cashOffer: parseInt(event.target.value)})}
              />
            </Col>
            <Col sm="6">
            <Form.Control
                size="sm"
                className="cst-ig mt-1 mb-3"
                min={0}
                max={playersCash[otherPlayerId]}
                placeholder="Cash Receive"
                aria-label="Cash Receive"
                type="number"
                onChange={event => this.setState({cashReceive: parseInt(event.target.value)})}
              />
            </Col>
          </Row>
          <Button size="sm" variant="primary" className="cst-btn" type="button" onClick={() => {
            publish([[otherPlayerId,cashOffer,actionProps,cashReceive,otherActionProps]]);
          }}>
            Submit
          </Button>
        </Card.Body>
        <Card.Footer>Time Remaining: <strong>{convertTimer(timeout)}</strong></Card.Footer>
      </Card>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  setOtherPlayerId: otherPlayerId =>
    dispatch(setOtherPlayerId(otherPlayerId)),
  setActionProps: actionProps =>
  dispatch(setProps({
    actionProps: actionProps
  })),
  setOtherActionProps: otherActionProps =>
  dispatch(setProps({
    otherActionProps: otherActionProps
  }))
});

const mapStateToProps = state => {
  return {
    myId: state.myId,
    players: state.players,
    turnNumber: state.turnNumber,
    properties: state.properties,
    playersCash: state.playersCash,
    timeout: state.timeout,
    otherPlayerId: state.otherPlayerId,
    actionProps: state.actionProps,
    otherActionProps: state.otherActionProps
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Trade);