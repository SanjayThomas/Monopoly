import React, { Component } from "react";
import { connect } from "react-redux";
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { convertTimer } from "utils";
import { setProps } from "redux/actions";

class Unmortgage extends Component {

  constructor(props, context) {
    super(props, context);

    const { myId, playersCash, setActionCash, publish } = props;

    this.state = {
      timeout: props.timeout
    };

    setActionCash(playersCash[myId]);
    
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
    const { turnNumber, actionProps, setActionProps, actionCash, properties, publish } = this.props;
    const { timeout } = this.state;

    return (
      <Card className="text-center">
        <Card.Header>Turn #{turnNumber}</Card.Header>
        <Card.Body>
          <Card.Title>Do you want to unmortgage any properties?</Card.Title>
          {actionProps.length === 0 && <p>Select properties you own to unmortgage them.</p>}
          {actionProps.map((construct,i) => {
            var initials = properties[construct].name.match(/\b\w/g) || [];
            initials = ((initials.shift() || '') + (initials.pop() || ''));
            return (<ButtonGroup key={i} size="sm" className="construct-group">
                      <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                        style={{ paddingRight: '2px' }}>
                        {initials} ${properties[construct].price}
                      </Button>
                      <Button className={`pb-sm-0 pt-sm-0 ${properties[construct].monopoly}`}
                        onClick={() => {
                          const newActionCash = actionCash - parseInt(properties[construct].price/2);
                          setActionProps(actionProps.filter((fv,fi) => fi!==i), newActionCash);
                        }}>
                        <FontAwesomeIcon icon={faTimes} />
                      </Button>
                    </ButtonGroup>);
          })
          }
          <h6>You would have ${actionCash} left.</h6>
          <Button variant="primary" className="cst-btn" type="button" onClick={ () => {
            publish([actionProps]);
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
  setActionProps: (actionProps,actionCash) =>
  dispatch(setProps({
    actionProps: actionProps,
    actionCash: actionCash
  })),
  setActionCash: actionCash =>
  dispatch(setProps({
    actionCash: actionCash
  }))
});

const mapStateToProps = state => {
  return {
    myId: state.myId,
    turnNumber: state.turnNumber,
    properties: state.properties,
    playersCash: state.playersCash,
    timeout: state.timeout,
    actionCash: state.actionCash,
    actionProps: state.actionProps
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Unmortgage);