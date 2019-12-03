import React, { Component } from "react";
import { connect } from "react-redux";
import Table from 'react-bootstrap/Table';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Badge from 'react-bootstrap/Badge';
import Alert from 'react-bootstrap/Alert';

import { setProp } from "../redux/actions.js";

import { CopyClipboard } from './copyClipboard.js';
import { GAME_TYPE_TEXT, fetchEndpoint, uiupdatesEndpoint } from './constants.js';

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
    else if (data[0] === 1 || data[0] === 2) {
      let { cGames, jGames } = this.state;
      for (let cGame of cGames) {
        if (cGame.tourId === data[1]) {
          cGame.status = data[0];
        }
      }
      for (let jGame of jGames) {
        if (jGame.tourId === data[1]) {
          jGame.status = data[0];
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

  getStatusContent = (game) => {
    // game status content
    let timerContent = '';

    if (game.status === 0) {
      if (game.expireTime > 0) {
        let joinedCount = 0;
        if (game.jPlayers) {
          joinedCount = game.jPlayers.length;  
        }

        timerContent = (<div>
                  <p>Game has not started. Will expire in: {this.convertTimer(game.expireTime)}</p>
                  <p>{joinedCount}/{game.noPlayers} players have joined.</p>
                  </div>);
      }
      else {
        timerContent = <p>Game has Expired!</p>;
      }
    }
    else if (game.status === 1) timerContent = <p>The game has started.</p>;
    else timerContent = <p>The game has been completed.</p>;

    return timerContent;
  }

  render() {
    const { cGames, jGames, fetchCompleted } = this.state;
    const { fetchNew } = this.props;

    return (
      <Row>
      <Col md={2}></Col>
      <Col md={8}>
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
                  <th># Players</th>
                  <th># Games</th>
                  <th>Game Details</th>
                  {fetchNew && <th>Game Status</th>}
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
                  <td style={{padding:0}}>
                    <Table striped bordered style={{margin:0}}>
                      <tbody>
                        <tr style={{fontWeight: 'bold'}}><td className="detail_row">Games Completed</td><td className="detail_row">{game.finishedGames}/{game.noGames}</td></tr>
                        {game.jPlayers.map((jPlayer, jIndex) => {
                          const variants = ['success', 'danger', 'warning', 'info', 'secondary', 'dark' ];
                          return (<tr key={jIndex}><td className="detail_row">
                            <Badge pill key={jIndex} variant={variants[jIndex]} className="player_pill">
                              {jPlayer[0]}
                            </Badge>
                          </td><td className="detail_row">{jPlayer[1]}</td></tr>);
                        })}
                      </tbody>
                    </Table>
                  </td>
                  {fetchNew && <td>{this.getStatusContent(game)}</td>}
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
                  <th>ID</th>
                  <th>Game Type</th>
                  <th># Players</th>
                  <th># Games</th>
                  <th>Game Details</th>
                  {fetchNew && <th>Game Status</th>}
                </tr>
              </thead>
              <tbody>
                {jGames.map((game, index) => {
                return (
                <tr key={index} onClick={log}>
                  <td>{index+1}</td>
                  <td style={{textAlign:'center'}}><CopyClipboard name={game.tourId+" "+this.props.sessionId}/></td>
                  <td>{GAME_TYPE_TEXT[game.tourType]}</td>
                  <td>{game.noPlayers}</td>
                  <td>{game.noGames}</td>
                  <td style={{padding:0}}>
                    <Table striped bordered style={{margin:0}}>
                      <tbody>
                        <tr style={{fontWeight: 'bold'}}><td className="detail_row">Games Completed</td><td className="detail_row">{game.finishedGames}/{game.noGames}</td></tr>
                        {game.jPlayers.map((jPlayer, jIndex) => {
                          const variants = ['success', 'danger', 'warning', 'info', 'secondary', 'dark' ];
                          return (<tr key={jIndex}><td className="detail_row">
                            <Badge pill key={jIndex} variant={variants[jIndex]} className="player_pill">
                              {jPlayer[0]}
                            </Badge>
                          </td><td className="detail_row">{jPlayer[1]}</td></tr>);
                        })}
                      </tbody>
                    </Table>
                  </td>
                  {fetchNew && <td>{this.getStatusContent(game)}</td>}
                </tr>
                );
                })}
              </tbody>
            </Table>
          </div>
        }
      </div>
      </Col>
      <Col md={2}></Col>
      </Row>
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