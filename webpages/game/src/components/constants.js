// Create Game Types
export const ONE_OFF = 0;
export const BRACKET = 1;
export const ROUND_ROBIN = 2;

export const PAGE_TYPES = {
  signin             : 0,
  create_solo        : 1,
  create_bracket     : 2,
  create_round_robin : 3,
  show_all           : 4,
  game_details       : 5,
  find_games         : 6,
  show_old			 : 7
};

export const GAME_TYPE_TEXT = ['One-Off Game','Bracket Tournament','Round Robin Tournament'];

export const TEAM_BOARDWALK = 'Team Boardwalk';

export const url = "ws://localhost:80/ws";
export const signinEndpoint = "com.monopoly.signin";
export const signoutEndpoint = "com.monopoly.signout";
export const createEndpoint = "com.monopoly.create_game";
export const fetchEndpoint = "com.monopoly.fetch_games";
export const joinEndpoint = "com.game{}.joingame";
export const uiupdatesEndpoint = "com.game{}.uiupdates";

// Specify the Google Client ID here
// More info can be found here:
// https://developers.google.com/identity/sign-in/web/sign-in
export const CLIENT_ID = '';
