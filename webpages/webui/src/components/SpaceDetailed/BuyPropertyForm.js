import React from "react";
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";

const BuyPropertyForm = ({ buyOutEndpoint, handleClose }) => {
  return (
    <Container>
      <Form.Label as="legend" column>
        Buy Property?
      </Form.Label>
      <Form.Check
        onChange={event => {
          window.session.publish(buyOutEndpoint, [true]);
          handleClose();
        }}
        type="radio"
        label="Yes"
        name="formHorizontalRadios"
        id="formHorizontalRadios1"
      />
      <Form.Check
        onChange={event => {
          window.session.publish(buyOutEndpoint, [false]);
          handleClose();
        }}
        type="radio"
        label="No"
        name="formHorizontalRadios"
        id="formHorizontalRadios2"
      />
    </Container>
  );
};

export default BuyPropertyForm;
