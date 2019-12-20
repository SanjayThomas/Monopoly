import React, { Component } from "react";
import { connect } from "react-redux";
import Space from "./Space";
import { range } from "utils";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";
import { setSelectedPropIndex, togglePropertyModal } from "redux/actions";
import "./style.css";

class Board extends Component {
  getPlayersOnPosition = index => {
    const { players, playersPositions } = this.props;
    let present = [];

    for (let i = 0; i < players.length; i++) {
      if (index === playersPositions[players[i]]) {
        present.push(i);
      }
    }
    return present;
  };

  getOwnerIndex = space => {
    const { players } = this.props;
    if ('ownerId' in space) {
      return players.indexOf(space.ownerId);
    }
    return -1;
  };

  getSpaceProps = index => {
    const {
      properties,
      setSelectedPropertyIndex,
      togglePropertyModal
    } = this.props;
    const space = properties[index];
    const key = index;
    const ownerIndex = this.getOwnerIndex(space);
    const playersOnPosition = this.getPlayersOnPosition(index);

    return {
      index,
      space,
      key,
      playersOnPosition,
      ownerIndex,
      setSelectedPropertyIndex,
      togglePropertyModal
    };
  };

  render() {
    const { getSpaceProps } = this;
    const { properties, selectedPropertyIndex } = this.props;

    return (
      <div className="board">
          <div className="middle-board">
            <GameInfo properties={properties} selectedPropertyIndex={selectedPropertyIndex}/>
            <PlayerActions/>
          </div>

          {/* Actual Grids go here */}
          <Space {...getSpaceProps(0)} />

          {/* Bottom Section */}
          <div className="board-row horizontal-board-row bottom-board-row">
            {range(9).map(index => (
              <Space {...getSpaceProps(10 - (index + 1))} />
            ))}
          </div>

          <Space {...getSpaceProps(10)} />

          {/* Left Section */}
          <div className="board-row vertical-board-row left-board-row">
            {range(9).map(index => (
              <Space {...getSpaceProps(20 - (index + 1))} />
            ))}
          </div>

          <Space {...getSpaceProps(20)} />

          {/* Top Section */}
          <div className="board-row horizontal-board-row top-board-row">
            {range(9).map((prop, index) => (
              <Space {...getSpaceProps(21 + index)} />
            ))}
          </div>

          <Space {...getSpaceProps(30)} />

          {/* Right Section */}
          <div className="board-row vertical-board-row right-board-row">
            {range(9).map((prop, index) => (
              <Space {...getSpaceProps(31 + index)} />
            ))}
          </div>
          {/* End of Game Playing Grids */}
        </div>
    );
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setSelectedPropertyIndex: selectedPropertyIndex =>
      dispatch(setSelectedPropIndex(selectedPropertyIndex)),
    togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
      dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex))
  };
};

const mapStateToProps = state => {
  return {
    players: state.players || [],
    properties: state.properties,
    candidates: state.candidates || [],
    playersPositions: state.playersPositions,
    selectedPropertyIndex: state.selectedPropertyIndex
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Board);
