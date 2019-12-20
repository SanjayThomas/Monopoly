import React from "react";
import { getColors } from "utils";

const Space = ({
  space,
  setSelectedPropertyIndex,
  index,
  playersOnPosition,
  ownerIndex,
  togglePropertyModal
}) => {
  const { monopoly, price, name } = space;
  const colors = getColors();
  return (
    <div
      onClick={() => {setSelectedPropertyIndex(index);}} //togglePropertyModal(true, index);}}
      className={`space ${space.class}`}
    >
      <div className={`${ownerIndex !== -1 ? `${colors[ownerIndex]}-owner` : ""} monopoly-box`}>
        {monopoly && <div className={`color-bar ${monopoly}`} />}
        {name && <div className="name">{name}</div>}

        {playersOnPosition.map((v,i) => {
          return <div key={i} className={`center-block agent-present ${colors[v]}-agent`} />;
        })
        }
        {price && <div className="price">Price ${price}</div>}
      </div>
    </div>
  );
};

export default Space;
