import React from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import { toggleJailDecisionModal } from "redux/actions";

const JailDecision = ({
  showJailDecisionModal,
  jailDecisionEndpoint,
  toggleJailDecisionModal
}) => {
  return (
    showJailDecisionModal && (
      <Modal show={showJailDecisionModal}>
        <Modal.Header>
          <Modal.Title>How do you want Get out of Jail</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>
            <Button
              onClick={() => {
                window.session.publish(jailDecisionEndpoint, ["R"]);
                toggleJailDecisionModal(false);
              }}
              variant="success"
              style={{ marginTop: "15px", marginBottom: "15px" }}
              block
            >
              Roll a Double
            </Button>
            <Button
              onClick={() => {
                window.session.publish(jailDecisionEndpoint, ["P"]);
                toggleJailDecisionModal(false);
              }}
              variant="warning"
              style={{ marginBottom: "15px" }}
              block
            >
              Pay $50
            </Button>
            <Button
              onClick={() => {
                window.session.publish(jailDecisionEndpoint, ["C", 41]);
                toggleJailDecisionModal(false);
              }}
              variant="secondary"
              style={{ marginTop: "15px", marginBottom: "15px" }}
              block
            >
              Use Get Out of Jail Card
            </Button>
          </Container>
        </Modal.Body>
      </Modal>
    )
  );
};

const mapDispatchToProps = dispatch => {
  return {
    toggleJailDecisionModal: showJailDecisionModal =>
      dispatch(toggleJailDecisionModal(showJailDecisionModal))
  };
};

const mapStateToProps = state => {
  return {
    showJailDecisionModal: state.showJailDecisionModal,
    jailDecisionEndpoint: state.endpoints.JAIL_OUT
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(JailDecision);
