import React from "react";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";

const MiddleBoard = props => {
  const { phase, myId, playersCash } = props;
  return (
    <div className="middle-board">
      <GameInfo playersCash={playersCash} myId={myId} />
      <PlayerActions phase={phase} />
    </div>
  );
};

export default MiddleBoard;
