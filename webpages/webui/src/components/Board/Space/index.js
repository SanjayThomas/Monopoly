import React from "react";

const Space = ({
  highlighted,
  space,
  togglePropertyModal,
  index,
  playersOnPosition,
  owned
}) => {
  const { monopoly, price, name } = space;
  return (
    <div
      onClick={() => togglePropertyModal(true, index)}
      className={`space ${space.class}  ${highlighted ? "highlight" : ""}`}
    >
      <div
        className={`${owned.owned ? `${owned.owner}-owner` : ""} monopoly-box`}
      >
        {monopoly && <div className={`color-bar ${monopoly}`} />}
        {name && <div className="name">{name}</div>}

        {playersOnPosition["human"] && (
          <div className={"center-block human-present"} />
        )}
        {playersOnPosition["robot"] && (
          <div className={"center-block robot-present"} />
        )}
        {price && <div className="price">Price ${price}</div>}
      </div>
    </div>
  );
};

export default Space;
