import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const GameInfo = ({ properties, selectedPropertyIndex }) => {
  let space = {};

  if (selectedPropertyIndex !== -1) {
    space = properties[selectedPropertyIndex];
  }

  let houses = 0, hotel = 'Not Present', ownerId = undefined, rent = [];
  if ('houses' in space) {
    if (houses > 4) hotel = 'Present';
    else houses = space.houses;
  }
  if ('ownerId' in space) {
    ownerId = space.ownerId;
  }
  if ('rent' in space) {
    rent = space.rent;
  }
    

  return (
    <div className="current-player-info">
      <h2 className="label">Currently Selected Property</h2>
      {Object.keys(space).length > 0 && <Container>
        <Row className="show-grid">
          <Col xs={6} md={12}>
            <span className="space-label"> Owner : </span>
            {ownerId ? ownerId : "Unowned"}
          </Col>
        </Row>
        <Row className="show-grid">
          <Col xs={6} md={6}>
            <span className="space-label"> Houses : </span> {houses}
          </Col>
          <Col xs={6} md={6}>
            <span className="space-label"> Hotels : </span> {hotel}
          </Col>
        </Row>
        <Row className="show-grid">
          <Col xs={6} md={6}>
            <span className="space-label"> Price : </span> ${space.price}
          </Col>
        </Row>
        <Row className="show-grid">
          {rent.length &&
            rent.map((item, index) => {
              return (
                <Col key={index} xs={6} md={6}>
                  <span className="space-label">
                    {" "}
                    Rent
                    {index === 0
                      ? " : "
                      : index < 5
                      ? `${index} House: `
                      : "Rent Hotel : "}
                  </span>
                  ${item}
                </Col>
              );
            })}
        </Row>
      </Container>}
    </div>
  );
};

export default GameInfo;
