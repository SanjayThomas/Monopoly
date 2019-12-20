import React, { Component } from "react";
import { connect } from "react-redux";
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Button from "react-bootstrap/Button";
import "./styles.css";

class UpdatesPanel extends Component {

  render() {
    const { myId, players, playersCash, bankrupt, setGameAndSession, joinGame } = this.props;

    return (
    <div>
      <Form style={{width:"400px",float:"left",marginLeft:"150px",marginTop:"40px", marginBottom:"100px"}}>
          <Form.Group controlId="formGroupPlayers">
            <Form.Label>Game ID, Session ID</Form.Label>
            <Form.Control
              placeholder="<game id> <session id>"
              onChange={event => {
                  let str = event.target.value;
                  if (str.length > 0) {
                    const ids = str.split(" ");
                    setGameAndSession(ids[0],ids[1]);
                  }
                }
              } />
          </Form.Group>
          <Button variant="primary" onClick={() => { 
            joinGame();
          }}>
            Start Game
          </Button>
        </Form>
        <div className="updates-panel">
    <Tabs fill defaultActiveKey="status" id="updates-panel">
      <Tab eventKey="status" title="Player Status">
        <div className="sub-panel">
          <div className="player-card">
            {players.length === 0 && <h6>Start the game to show player status.</h6>}
            <Table striped bordered hover>
              <tbody>
                {players.map((player,i) => {
                  return <tr key={i}>
                            <th>
                              <h6>
                                {player}
                                {player === myId && <span> (You)</span>}
                                {bankrupt[player] && <span style={{color:"red"}}> (Lost)</span>}
                              </h6>
                            </th>
                            <td>
                              <h6>{playersCash[player]}</h6>
                            </td>
                         </tr>;
                })}
              </tbody>
            </Table>
          </div>
        </div>
      </Tab>
      {false && <Tab eventKey="Activity" title="Activity">
        <div className="sub-panel">
          <p style={{textDecoration: "underline", fontSize: "16px"}}>Turn 10:</p>
          <p style={{textDecoration: "underline", fontSize: "14px"}}>Player 2:</p>
          <p>The player rolled a 4 and a 2.</p>
          <p>The player landed on Vermont Avenue.</p>
          <p>The player unmortgages St. Charles Place spending $25.</p>
          <p>The player decides to buy it spending $120.</p>
          <p style={{textDecoration: "underline", fontSize: "14px"}}>Player 3:</p>
          <p>The player rolled a 4 and a 2.</p>
          <p>The player landed on Vermont Avenue.</p>
          <p>The player unmortgages St. Charles Place spending $25.</p>
          <p>The player decides to buy it spending $120.</p>
        </div>
        
      </Tab>}
    </Tabs>
    </div>
    </div>
    );
  }
};

const mapStateToProps = state => {
  return {
    myId: state.myId,
    players: state.players || [],
    playersCash: state.playersCash,
    bankrupt: state.bankrupt
  };
};

export default connect(
  mapStateToProps
)(UpdatesPanel);