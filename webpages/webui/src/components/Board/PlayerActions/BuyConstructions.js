import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Form from "react-bootstrap/Form";
import InputGroup from 'react-bootstrap/InputGroup';
import Button from "react-bootstrap/Button";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Badge from 'react-bootstrap/Badge';
import { convertTimer } from "utils";

class BuyConstructions extends Component {

  constructor(props, context) {
    super(props, context);

    const { playersCash, myId, publish } = props;

    this.state = {
      constructions: [],
      timeout: props.timeout,
      currentHouses: 0,
      actionCash: playersCash[myId]
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

  checkCash = (selectedPropertyIndex, currentHouses, actionCash) => {
    const { properties } = this.props;

    console.log(actionCash < properties[selectedPropertyIndex].build_cost * currentHouses);
    if (actionCash < properties[selectedPropertyIndex].build_cost * currentHouses) return true;
    return false;
  }

  componentWillUnmount() {
    // preventing state update after leaving component
    if (this.timerID) clearInterval(this.timerID);
  }
  
  render() {
    const { turnNumber, selectedPropertyIndex, properties, buyCandidates, publish } = this.props;
    const { constructions, timeout, currentHouses, actionCash } = this.state;

    let houses = 0;
    if (buyCandidates.includes(selectedPropertyIndex)) {
      houses = properties[selectedPropertyIndex].houses;
    }

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Do you want to buy houses/hotels?</Card.Title>
          {constructions.length === 0 && <p>Select properties where you want to construct houses/hotels.</p>}
          {constructions.map((construct,i) => {
            var initials = properties[construct[0]].name.match(/\b\w/g) || [];
            initials = ((initials.shift() || '') + (initials.pop() || ''));
            return (<ButtonGroup key={i} size="sm" className="construct-group">
                      <Button className={`pb-sm-0 pt-sm-0 ${properties[construct[0]].monopoly}`}
                        style={{paddingRight: '2px'}}>{initials} ${properties[construct[0]].price}
                        <Badge pill variant="light" style={{marginLeft: '2px'}}>{construct[1]}</Badge>
                      </Button>
                      <Button className={`pb-sm-0 pt-sm-0 ${properties[construct[0]].monopoly}`}
                        onClick={() => this.setState((state,props) => ({
                          constructions: constructions.filter((fv,fi) => fi!==i),
                          actionCash: state.actionCash + (properties[construct[0]].build_cost * construct[1])
                      }))}>
                        <FontAwesomeIcon icon={faTimes} />
                      </Button>
                    </ButtonGroup>);
          })
          }
          <InputGroup className="cst-ig mt-2 mb-3">
            <Form.Control
              min={houses}
              max={5}
              placeholder="Houses to Buy"
              aria-label="Houses to Buy"
              type="number"
              value={currentHouses}
              onChange={event => this.setState({currentHouses: event.target.value})}
            />
            <InputGroup.Append>
              <Button variant="outline-primary" type="button"
                disabled={!buyCandidates.includes(selectedPropertyIndex)}
                onClick={ () => {
                  const len = constructions.filter(construct => 
                    construct[0] === selectedPropertyIndex)
                    .length;

                  if (len === 0 && currentHouses > 0 && buyCandidates.includes(selectedPropertyIndex)) {
                    this.setState((state,props) => ({
                      constructions: [...constructions, [selectedPropertyIndex,currentHouses]],
                      actionCash: state.actionCash - (properties[selectedPropertyIndex].build_cost * currentHouses)
                    }));
                  }
                }
              }>
              Add
              </Button>
            </InputGroup.Append>
          </InputGroup>
            <h6>You would have ${actionCash} left.</h6>
            <Button variant="primary" className="cst-btn" type="button" onClick={ () => {
              console.log(constructions);
              publish([constructions]);
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
    resUri: state.resUri,
    turnNumber: state.turnNumber,
    playersCash: state.playersCash,
    properties: state.properties,
    timeout: state.timeout,
    selectedPropertyIndex: state.selectedPropertyIndex,
    buyCandidates: state.buyCandidates,
  };
};

export default connect(
  mapStateToProps
)(BuyConstructions);