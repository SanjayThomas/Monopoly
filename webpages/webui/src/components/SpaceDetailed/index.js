import React, { useState } from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import SpaceInfo from "./SpaceInfo";
import { togglePropertyModal } from "redux/actions";

const SpaceDetailed = ({
  selectedPropertyIndex,
  showPropertyModal,
  properties,
  phase,
  playerAction,
  togglePropertyModal
}) => {
  const handleClose = () => {
    togglePropertyModal(false);
  };

  const space = properties[selectedPropertyIndex];
  const closeButton = {
    closeButton: !buyMortgage
  };

  return (
    showPropertyModal && (
      <Modal show={showPropertyModal} onHide={() => handleClose()}>
        <Modal.Header style={{ background: space.monopoly }} {...closeButton}>
          <Modal.Title>{space.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>
            {/* Space info */}
            <SpaceInfo space={space} />
          </Container>
        </Modal.Body>
      </Modal>
    )
  );
};

const mapDispatchToProps = dispatch => {
  return {
    togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
      dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex))
  };
};

const mapStateToProps = state => {
  return {
    selectedPropertyIndex: state.selectedPropertyIndex,
    showPropertyModal: state.showPropertyModal,
    phase: state.phase,
    playerAction: state.playerAction,
    properties: state.properties
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SpaceDetailed);
