import React from "react";
import { getPlayerName } from "utils";

const GameInfo = ({ playersCash, myId }) => {
  return (
    <div className="current-player-info">
      <h2 className="label">Player Info</h2>
      {Object.keys(playersCash).map((playerId, index) => {
        return (
          <div
            style={{
              marginBottom: "15px",
              fontWeight: "bold",
              fontSize: "18px"
            }}
            key={index}
          >
            {getPlayerName(myId, playerId)} :{playersCash[playerId]}
          </div>
        );
      })}
    </div>
  );
};

export default GameInfo;
