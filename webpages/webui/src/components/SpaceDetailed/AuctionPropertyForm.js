import React, { useState } from "react";
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

const AuctionPropertyForm = ({ auctionEndpoint, handleClose }) => {
  const [bid, setBid] = useState(0);
  return (
    <Container>
      <Form.Group controlId="autionProperty">
        <Form.Label>Auction Property</Form.Label>
        <Form.Control
          min={0}
          type="number"
          value={bid}
          onChange={event => setBid(event.target.value)}
          placeholder="Enter an amount to bid"
        />
      </Form.Group>
      <Button
        variant="danger"
        onClick={() => {
          window.session.publish(auctionEndpoint, [bid]);
          handleClose();
        }}
      >
        Bid Now
      </Button>
    </Container>
  );
};

export default AuctionPropertyForm;
