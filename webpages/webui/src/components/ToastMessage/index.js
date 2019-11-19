import React from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import { toggleToastMessageModal } from "redux/actions";

const ToastMessage = ({
  toggleToastMessageModal,
  showToastMessage,
  toastTitle,
  toastMessage
}) => {
  return (
    showToastMessage && (
      <Modal
        show={showToastMessage}
        onHide={() => toggleToastMessageModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>{toastTitle}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>{toastMessage}</Container>
        </Modal.Body>
      </Modal>
    )
  );
};

const mapDispatchToProps = dispatch => {
  return {
    toggleToastMessageModal: showToastMessage =>
      dispatch(toggleToastMessageModal(showToastMessage))
  };
};

const mapStateToProps = state => {
  return {
    showToastMessage: state.showToastMessage,
    toastMessage: state.toastMessage,
    toastTitle: state.toastTitle
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ToastMessage);
