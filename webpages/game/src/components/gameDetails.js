import React, { Component } from "react";
import { connect } from "react-redux";
import Jumbotron from 'react-bootstrap/Jumbotron';
import Table from 'react-bootstrap/Table';
import Badge from 'react-bootstrap/Badge';
import Alert from 'react-bootstrap/Alert';

import { CopyClipboard } from './copyClipboard.js';
import { GAME_TYPE_TEXT, fetchEndpoint, uiupdatesEndpoint } from './constants.js';

class GameDetails extends Component {

  constructor(props, context) {
    super(props, context);

    this.state = { tourId: null, expireTime: 0, fetchCompleted: false };

    if ( !('currentGameId' in props) || (props.currentGameId==="ERROR") ) {
      alert("The game could not be opened. Please contact the admins.");
      return;
    }

    if (window.session === undefined) {
      console.log("The session hasn't been initialized yet.");
      return;
    }

    window.session.call(fetchEndpoint, [props.sessionId, 0, props.currentGameId]).then(
    data => {
      console.log(data);
      if (data.length > 0) {
        let newState = { ...data[0] };
        
        //if ('jPlayers' in data[0]) {
        //  newState.colorIndices = this.genColorIndices(data[0].jPlayers);
        //}

        if ('expireTime' in newState && newState.expireTime > 0) {
          this.timerID = setInterval(
          () => {
            this.setState((state, props) => ({
              expireTime: state.expireTime - 1 > 0 ? state.expireTime - 1 : 0
            }));

            if (this.state.expireTime === 0) {
              clearInterval(this.timerID);
              console.log("Timer expired!");
            }
          },1000);
        }

        let subFunc = (subscription) => { this.subId = subscription; }
        window.session.subscribe(uiupdatesEndpoint.replace("{}",data['tourId']),this.uiupdates).then(subFunc.bind(this));
        this.setState(newState);
      }
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
      this.setState((state, props) => ({
        finishedGames: data[2], jPlayers: data[3]
      }));
    }
    else if (data[0] === 1 || data[0] === 2) {
      this.setState((state, props) => ({
        status: data[0]
      }));
    }
  }

  componentWillUnmount() {
    // preventing state update after leaving component
    if (this.timerID) clearInterval(this.timerID);
    if (this.subId) window.session.unsubscribe(this.subId);
  }

  genColorIndices = jPlayers => {
    let colorIndices = [];
    let prevIndex = null, index;
    
    let i = 0;
    while(i<jPlayers.length) {
      index = Math.floor(Math.random() * 4);
      if (index !== prevIndex) {
        colorIndices.push(index);
        prevIndex = index;
        i++;
      }
    }

    return colorIndices;
  };

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
    let { tourId, tourType, noPlayers, noGames, jPlayers, creator, expireTime,
      finishedGames, status, fetchCompleted, allowHumans } = this.state;

    // game status content
    let timerContent = '<td></td>';
    let statusContent = '<td></td>';
    if (status === 0) {
      if (expireTime > 0) {
        timerContent = <p>Game has not started. Will expire in: {this.convertTimer(expireTime)}</p>;
      }
      else {
        timerContent = <p>Game has Expired!</p>;
      }
    }
    else if (status === 1) timerContent = <p>The game has started.</p>;
    else timerContent = <p>The game has been completed.</p>;
    if (!jPlayers || jPlayers.length === 0) {
      statusContent = <p>No player has joined.</p>;
    }
    else {
      const variants = ['success', 'danger', 'warning', 'info', 'secondary', 'dark' ];
      statusContent = <Table responsive>
                      <tbody>
                      <tr style={{fontWeight: 'bold'}}><td>Total # Games</td><td>{finishedGames}/{noGames}</td></tr>
                      {jPlayers.map((jPlayer, jIndex) => {
                        return <tr key={jIndex}><td>
                          <Badge pill key={jIndex} variant={variants[jIndex]} className="player_pill">
                          {jPlayer[0]}
                          </Badge>
                          </td><td>{jPlayer[1]}/{noGames}</td></tr>;
                      })}
                      </tbody>
                      </Table>;
    }


    return (
      <div>
      { (fetchCompleted && tourId === null) && <Alert variant="danger">
        <Alert.Heading>Game not found</Alert.Heading>
        <p>This could be due to one of the following reasons:</p>
        <p>1) The game has timed out.</p> 
        <p>2) The provided game ID is invalid.</p>
        <p>Please try creating another game.</p>
        </Alert>}
      { tourId &&
      <div>
      <Jumbotron style={{paddingTop:'2rem'}}>
        <h2 style={{ textDecoration: 'underline', marginBottom: '2rem' }}>Game Details</h2> 
        <Alert variant='success'>
        To join any game, you need specify the tourId and your current session ID as arguments for the agent.<br/>
        Invoke your agent as: python agent.py &lt;gameID&gt; &lt;sessionID&gt;<br/>
        Click on the Clipboard icon next to the Game ID for the game you want to join to copy the string "&lt;gameID&gt; &lt;sessionID&gt;"
        </Alert>
        {allowHumans!==0 && <Alert variant='success'>
        To join this game as a human player, click on this URL: <a href="http://monopoly-ai.com/sbu_agent/" target="_blank">http://monopoly-ai.com/sbu_agent/</a>
        The human player interface requires the game ID to be entered to join this game. Copy the game ID as per the instructions above.
        </Alert>}
        <Table borderless>
          <tbody>
          <tr>
            <td>Game ID: </td>
            <td><span style={{marginRight:'1rem'}}>{tourId}</span><CopyClipboard name={tourId+" "+this.props.sessionId}/></td>
          </tr>
          <tr>
            <td>Game Type: </td>
            <td>{GAME_TYPE_TEXT[tourType]}</td>
          </tr>
          <tr>
            <td>Created by: </td>
            <td>{creator}</td>
          </tr>
          <tr>
            <td>Total number of players: </td>
            <td>{noPlayers}</td>
          </tr>
          <tr>
            <td>Total number of games:</td>
            <td>{noGames}</td>
          </tr>
        </tbody>
        </Table>
        <h4 style={{marginBottom: '1rem'}}>Game Status:</h4>
        {timerContent}
        {statusContent}
      </Jumbotron>
      </div>
      }
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    pageType: state.pageType,
    sessionId: state.sessionId,
    email: state.email
  };
};

export default connect(
  mapStateToProps
)(GameDetails);