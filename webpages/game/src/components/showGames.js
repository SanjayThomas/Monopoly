import React, { Component } from "react";
import { connect } from "react-redux";
import Table from 'react-bootstrap/Table';
import Badge from 'react-bootstrap/Badge';
import Button from "react-bootstrap/Button";
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';
import Alert from 'react-bootstrap/Alert';

import { setProp } from "../redux/actions.js";

import { CopyClipboard } from './copyClipboard.js';
import { GAME_TYPE_TEXT, TEAM_BOARDWALK, fetchEndpoint, joinEndpoint, uiupdatesEndpoint } from './constants.js';

function log() {
  console.log("hello");
}

class ShowGames extends Component {

  constructor(props, context) {
    super(props, context);

    this.state = { cGames: [], jGames: [], fetchCompleted: false };
    this.subIds = [];

    let payload = undefined;
    if (props.fetchNew) {
      payload = [props.sessionId,1,true];
    }
    else {
      payload = [props.sessionId,1,false];
    }
    console.log(payload);
    window.session.call(fetchEndpoint, payload).then(
    data => {
      console.log(data);
      this.setState((state, props) => ({
        fetchCompleted: true
      }));
      
      if (data.length < 2) return;

      let subFunc = (subscription) => { this.subIds.push(subscription); }
      this.setState({
        cGames: data[0],
        jGames: data[1]
      });

      for (let game of data[0]) {
        window.session.subscribe(uiupdatesEndpoint.replace("{}",game.tourId),this.uiupdates).then(subFunc.bind(this));
      }
      for (let game of data[1]) {
        window.session.subscribe(uiupdatesEndpoint.replace("{}",game.tourId),this.uiupdates).then(subFunc.bind(this));
      }

      this.timerID = setInterval(
      () => {
        let { cGames, jGames } = this.state;
        for (let cGame of cGames) {
          cGame.expireTime = (cGame.expireTime > 1) ? (cGame.expireTime - 1) : 0;
        }
        for (let jGame of jGames) {
          jGame.expireTime = (jGame.expireTime > 1) ? (jGame.expireTime - 1) : 0;
        }
        
        this.setState((state, props) => ({
          cGames: cGames, jGames: jGames
        }));
      },1000);
    },reason => {
      console.log("Failure reason:");
      console.log(reason);
      this.setState((state, props) => ({
        fetchCompleted: true
      }));
    });
  }

  uiupdates = data => {
    if (data === undefined || (data[0] === undefined)) return;
    data = data[0];

    if (data[0] === 0) {
      let { cGames, jGames } = this.state;
      for (let cGame of cGames) {
        if (cGame.tourId === data[1]) {
          cGame.finishedGames = data[2];
          cGame.jPlayers = data[3];
        }
      }
      for (let jGame of jGames) {
        if (jGame.tourId === data[1]) {
          jGame.finishedGames = data[2];
          jGame.jPlayers = data[3];
        }
      }
      
      this.setState((state, props) => ({
        cGames: cGames, jGames: jGames
      }));
    }
    else if (data[0] === 1) {
      let { cGames, jGames } = this.state;
      for (let cGame of cGames) {
        if (cGame.tourId === data[1]) {
          cGame.status = 1;
        }
      }
      for (let jGame of jGames) {
        if (jGame.tourId === data[1]) {
          jGame.status = 1;
        }
      }
      
      this.setState((state, props) => ({
        cGames: cGames, jGames: jGames
      }));
    }
  }

  componentWillUnmount() {
    // preventing state update after leaving component
    if (this.timerID) clearInterval(this.timerID);
    if (this.subIds){
      for (const subId of this.subIds) {
        window.session.unsubscribe(subId);
      }
    }
  }

  convertTimer = timer => {
    let min = Math.floor(timer/60);
    let sec = timer%60;

    if (sec < 10) {
      sec = "0" + sec;
    }
    if (min < 10) {
      min = "0" + min;
    }

    return min+":"+sec;
  };

  render() {
    const { cGames, jGames, fetchCompleted } = this.state;

    return (
      <div>
        {(fetchCompleted && cGames.length === 0 && jGames.length === 0) && <Alert variant='danger'>You have not started or joined any games.</Alert>}
        {(cGames.length > 0 || jGames.length > 0) &&
          <Alert variant='success'>
            To join any game, you need specify the tourId and your current session ID as arguments for the agent.<br/>
            Invoke your agent as: python agent.py &lt;gameID&gt; &lt;sessionID&gt;<br/>
            Click on the Clipboard icon in the ID column for the game you want to join to copy the string "&lt;gameID&gt; &lt;sessionID&gt;"
          </Alert>
        }
        {(cGames.length > 0) && 
          <div>
            <h4 style={{ textDecoration: 'underline' }}>Games I Started:</h4>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>#</th>
                  <th>ID</th>
                  <th>Game Type</th>
                  <th>Total Players</th>
                  <th>Games</th>
                  <th>Joined Players</th>
                  <th>Game Status</th>
                </tr>
              </thead>
              <tbody>
                {cGames.map((game, index) => {
                return (
                <tr key={index} onClick={log}>
                  <td>{index+1}</td>
                  <td style={{textAlign:'center'}}><CopyClipboard name={game.tourId+" "+this.props.sessionId}/></td>
                  <td>{GAME_TYPE_TEXT[game.tourType]}</td>
                  <td>{game.noPlayers}</td>
                  <td>{game.noGames}</td>
                  <td>
                  {
                    (game.jPlayers.length === 0) && "No player has joined"
                  }
                  {
                    game.jPlayers.map((player, jIndex) => {
                      const variants = ['success', 'danger', 'warning', 'info', 'secondary', 'dark' ];
                      // TODO: might need to change later
                      if (player === this.props.email) {
                        return (<Badge pill key={jIndex} variant={variants[jIndex]}
                          style={{marginRight: '2px',fontSize: '1rem'}}>
                          {player[0]}{false && <CopyClipboard name={game.currentAgentId} content="Copy Agent ID"/>}
                          </Badge>);
                      }
                      return (<Badge pill key={jIndex} variant={variants[jIndex]}
                        style={{marginRight: '2px',fontSize: '1rem'}}>{player[0]}</Badge>);
                    })
                  }
                  {
                    (false && !game.jPlayers.includes(this.props.email)) &&
                    (<Button variant="outline-primary" size="sm"
                      onClick={() => {
                        if (window.session === undefined) {
                          console.log("The session hasn't been initialized yet.")
                          return;
                        }
                        let uri = joinEndpoint.replace("{}",game.tourId);
                        window.session.call(uri, [this.props.sessionId]).then(
                        agentId => {
                          if (agentId === "ERROR") {
                            console.log("Error while joining the game.");
                          }
                          else {
                            console.log("Your agentId: "+agentId);
                            let { cGames, jGames } = this.state;
                            for (let cGame of cGames) {
                              if (cGame.tourId === game.tourId) {
                                cGame.jPlayers.push(this.props.email);
                                cGame.currentAgentId = agentId;
                              }
                            }
                            for (let jGame of jGames) {
                              if (jGame.tourId === game.tourId) {
                                jGame.jPlayers.push(this.props.email);
                                jGame.currentAgentId = agentId;
                              }
                            }
                            
                            this.setState((state, props) => ({
                              cGames: cGames, jGames: jGames
                            }));
                          }
                        });
                      }}
                      style={{marginRight: '4px', display:'inline'}}>Join</Button>)
                  }
                  { false && (<DropdownButton id="add_our_agent"
                      variant="outline-primary"
                      title="Add Test Agent"
                      size="sm"
                      style={{marginRight: '2px', display:'inline'}}>
                        <Dropdown.Item eventKey="team_boardwalk">Team Boardwalk</Dropdown.Item>
                      </DropdownButton>)
                  }</td>
                  {(game.status === 0) ? 
                    (game.expireTime > 0 ? 
                      (<td>Expires in: {this.convertTimer(game.expireTime)}</td>) : (<td>Game has Expired!</td>)
                    ) : (<td>
                    <Table striped bordered>
                      <tbody>
                        <tr style={{fontWeight: 'bold'}}><td>Total # Games</td><td>{game.finishedGames}/{game.noGames}</td></tr>
                        {game.jPlayers.map((jPlayer, jIndex) => {
                          return (<tr key={jIndex}><td>{jPlayer[0]}</td><td>{jPlayer[1]}</td></tr>);
                        })}
                      </tbody>
                    </Table>
                    </td>)
                  }
                </tr>
                );
              })}
              </tbody>
            </Table>
          </div>
        }
        {(jGames.length > 0) && 
          <div>
            <h4 style={{ textDecoration: 'underline' }}>Games I have joined:</h4>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Game Type</th>
                  <th>Total Players</th>
                  <th>Games</th>
                  <th>Joined Players</th>
                  <th>Game Status</th>
                </tr>
              </thead>
              <tbody>
                {jGames.map((game, index) => {
                return (
                <tr key={index} onClick={log}>
                  <td>{index+1}</td>
                  <td>{GAME_TYPE_TEXT[game.tourType]}</td>
                  <td>{game.noPlayers}</td>
                  <td>{game.noGames}</td>
                  <td>{
                    game.jPlayers.map((player, jIndex) => {
                      const variants = ['success', 'danger', 'warning', 'info', 'secondary', 'dark' ];
                      return (<Badge pill key={jIndex} variant={variants[jIndex]}
                        style={{marginRight: '2px',fontSize: '1rem'}}>{player[0]}</Badge>);
                    })
                  }</td>
                  {(game.status === 0) ? 
                    (game.expireTime > 0 ? 
                      (<td>Expires in: {this.convertTimer(game.expireTime)}</td>) : (<td>Game has Expired!</td>)
                    ) : (<td>
                    <Table striped bordered>
                      <tbody>
                        <tr style={{fontWeight: 'bold'}}><td>Total # Games</td><td>{game.finishedGames}/{game.noGames}</td></tr>
                        {game.jPlayers.map((jPlayer, jIndex) => {
                          return (<tr key={jIndex}><td>{jPlayer[0]}</td><td>{jPlayer[1]}</td></tr>);
                        })}
                      </tbody>
                    </Table>
                    </td>)
                  }
                </tr>
                );
                })}
              </tbody>
            </Table>
          </div>
        }
      </div>
    );

  }
};

const mapDispatchToProps = dispatch => ({
  setPageType: pageType =>
    dispatch(setProp("pageType", pageType)),
  setCurrentGameId: currentGameId =>
    dispatch(setProp("currentGameId", currentGameId))
});

const mapStateToProps = state => {
  return {
    pageType: state.pageType,
    currentGameId: state.currentGameId,
    sessionId: state.sessionId,
    email: state.email
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ShowGames);