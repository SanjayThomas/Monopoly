import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const SpaceInfo = ({ space }) => {
  let { rent, houses, owned, ownerId, hotel } = space;
  rent = rent || [];
  houses = houses || 0;
  hotel = hotel ? "Present" : "Not Present";

  return (
    <div>
      <Row className="show-grid">
        <Col xs={6} md={12}>
          <span className="space-label"> Owner : </span>{" "}
          {owned ? ownerId : "Unowned"}
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
                    ? `House ${index} : `
                    : "Rent Hotel : "}
                </span>
                ${item}
              </Col>
            );
          })}
      </Row>
    </div>
  );
};

export default SpaceInfo;
