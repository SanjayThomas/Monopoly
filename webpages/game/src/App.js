import React, { Component } from "react";
import { connect } from "react-redux";
import Autobahn from "autobahn";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Dropdown from 'react-bootstrap/Dropdown';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Image from 'react-bootstrap/Image';
import Alert from 'react-bootstrap/Alert';

import './App.css';
import "bootstrap/dist/css/bootstrap.css";

import {
  PAGE_TYPES,
  CLIENT_ID,
  url,
  signinEndpoint,
  signoutEndpoint
} from './components/constants';
import { setProps } from "./redux/actions.js";

import CreateGame from './components/createGame';
import ShowGames from './components/showGames.js';
import GameDetails from './components/gameDetails.js';
import FindGames from './components/findGames.js';

import { GoogleLogin,GoogleLogout } from 'react-google-login';

class App extends Component {

  constructor(props, context) {
    super(props, context);
    window.session = null;
    this.subIds = [];
    this.state = {
      isSignedIn: false
    };
  }

  handleSelect = eventKey => {
    if (eventKey in PAGE_TYPES) {
      this.props.setPageType(PAGE_TYPES[eventKey]);
    }
    else{
      console.log("Not found: "+eventKey);
    }
  };

  failCallback = (error,details) => {
    console.log("Failure Error Code: "+error);
    console.log(details);
    alert("Google login/logout failed. Please try again.");
  };

  onSignIn = (googleUser) => {
    var profile = googleUser.getBasicProfile();

    if (window.session === undefined) {
      console.log("The session hasn't been initialized yet.");
      alert("Unexpected error. Please try signing in again.");
      return;
    }
    
    window.session.call(signinEndpoint, [profile.getEmail(), googleUser.getAuthResponse().id_token]).then(
    sessionId => {
      console.log('Session ID: ' + sessionId);
      this.setState({
        isSignedIn: true,
        givenName: profile.getGivenName(),
        email: profile.getEmail(),
        imageUrl: profile.getImageUrl()
      });
      this.props.setCreds(profile.getEmail(),sessionId);
    },reason => {
      alert("Backend server is down. Please contact the admins.");
    });
  }

  logout = () => {
    this.setState({
      isSignedIn: false,
      givenName: null,
      email: null,
      imageUrl: null
    });

    if (window.session === undefined) {
      console.log("The session hasn't been initialized yet.");
      alert("Unexpected error. Please try signing in again.");
      return;
    }
    
    window.session.call(signoutEndpoint, [this.state.email]).then(
    status => {
      console.log("Logged out");
    },reason => {
      alert("Backend server is down. Please contact the admins.");
    });
  }

  logoutButtonRender = (renderProps) => {
    return (<Dropdown.Item as="button" onClick={renderProps.onClick}>Logout</Dropdown.Item>);
  }

  pageRender = () => {
    const { pageType, currentGameId } = this.props;
    const { failCallback, onSignIn } = this;

    if (!this.state.isSignedIn) {
      return (<div>
              <Row style={{textAlign: 'center', marginTop: '28%'}}>
                <Col></Col>
                <Col><Alert variant='success'>Please Signin to access the games</Alert></Col>
                <Col></Col>
              </Row>
              <Row style={{textAlign: 'center', marginTop: '2%'}}>
                <Col></Col>
                <Col><GoogleLogin clientId={CLIENT_ID} onSuccess={onSignIn} onFailure={failCallback} isSignedIn={true}/></Col>
                <Col></Col>
              </Row>
              </div>);
    }

    switch(pageType) {
      case PAGE_TYPES.signin:
      return (<div>
              <Row style={{textAlign: 'center', marginTop: '28%'}}>
                <Col></Col>
                <Col><Alert variant='success'>Please Signin to access the games</Alert></Col>
                <Col></Col>
              </Row>
              <Row style={{textAlign: 'center', marginTop: '2%'}}>
                <Col></Col>
                <Col><GoogleLogin clientId={CLIENT_ID} onSuccess={onSignIn} onFailure={failCallback} isSignedIn={true}/></Col>
                <Col></Col>
              </Row>
              </div>);
      case PAGE_TYPES.create_solo:
      return (<CreateGame/>);
      case PAGE_TYPES.create_bracket:
      return (<CreateGame type={1}/>);
      case PAGE_TYPES.create_round_robin:
      return (<CreateGame type={2}/>);
      case PAGE_TYPES.show_all:
      return (<ShowGames key="new" fetchNew={true}/>);
      case PAGE_TYPES.game_details:
      return (<GameDetails currentGameId={currentGameId}/>);
      case PAGE_TYPES.find_games:
      return (<FindGames/>);
      case PAGE_TYPES.show_old:
      return (<ShowGames key="old" fetchNew={false}/>);
      default:
      return;
    }
  } 

  componentDidMount() {
    const realm = "realm1";

    const connection = new Autobahn.Connection({
     url,
     realm
    });

    connection.onopen = session => {
     window.session = session;
    };
    
    connection.open();
  }

  render() {
    
    const { isSignedIn, givenName, imageUrl } = this.state;
    const { handleSelect,failCallback,onSignIn,logout,logoutButtonRender, pageRender } = this;

    return (
      <div className="App">
        <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark" onSelect={handleSelect}>
          <Navbar.Brand href="/">Monopoly AI</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="mr-auto">
              <Nav.Link eventKey="create_solo">Start Game</Nav.Link>
              {false && <Dropdown as={Nav.Item}>
                  <Dropdown.Toggle
                    as={Nav.Link}>
                    Start Tournament
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                  <Dropdown.Item eventKey="create_round_robin">Round Robin</Dropdown.Item>
                  <Dropdown.Item eventKey="create_bracket">Tournament Tree</Dropdown.Item>
                  </Dropdown.Menu>
              </Dropdown>}
              <Nav.Link eventKey="show_all">Show my Games</Nav.Link>
              <Nav.Link eventKey="show_old">Show past Games</Nav.Link>
              <Nav.Link eventKey="find_games">Find Games</Nav.Link>
            </Nav>
            <Nav>
              {!isSignedIn && (
              <GoogleLogin
                clientId={CLIENT_ID}
                onSuccess={onSignIn}
                onFailure={failCallback}
                isSignedIn={true}
              />
              )}
              {isSignedIn && (
              <Dropdown alignRight id="userButton" as={Nav.Item} style={{marginRight:'2px'}}>
                  <Dropdown.Toggle as={Nav.Link}>
                    {givenName}
                    <Image src={imageUrl} roundedCircle style={{width: '32px', marginTop: '-4px', marginLeft: '6px'}}/>
                  </Dropdown.Toggle>
                <Dropdown.Menu>
                  {false && <Dropdown.Item eventKey="user_profile">Profile</Dropdown.Item>}
                  <GoogleLogout
                    clientId={CLIENT_ID}
                    render={logoutButtonRender}
                    onLogoutSuccess={logout}
                    onFailure={failCallback}/>
                </Dropdown.Menu>
              </Dropdown>
              )}
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Container fluid={true} style={{ marginTop: "4%", textAlign: 'left'}}>
          { pageRender() }
        </Container>
          
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  setPageType: pageType => dispatch(setProps({
    pageType: pageType
  })),
  setCreds: (email,sessionId) => dispatch(setProps({
    email: email,
    sessionId: sessionId
  }))
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
)(App);