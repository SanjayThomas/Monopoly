SET GLOBAL event_scheduler = ON;

DROP DATABASE IF EXISTS monopoly;
CREATE DATABASE monopoly;

USE monopoly;

CREATE TABLE IF NOT EXISTS user (
  id int(11) NOT NULL AUTO_INCREMENT,
  email varchar(255),
  sessionId varchar(64) DEFAULT NULL,
  lastActivity int(11) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email (email),
  UNIQUE KEY sessionId (sessionId)
);

CREATE EVENT remove_old_sessions
ON SCHEDULE EVERY 3 MINUTE
DO UPDATE user SET sessionId=NULL, lastActivity=NULL WHERE UNIX_TIMESTAMP(CURRENT_TIMESTAMP) - lastActivity > 1800;

/* status: 0=not started, 1=started, 2=finished */

CREATE TABLE IF NOT EXISTS tournament (
  id int(11) NOT NULL AUTO_INCREMENT,
  tourUID char(48) NOT NULL,
  tourType int(2) DEFAULT 0,
  noPlayers int(6) DEFAULT 2,
  noGames int(6) DEFAULT 100,
  noPpg int(2) DEFAULT NULL,
  createUserId int(11) NOT NULL,
  createTime int(11) NOT NULL,
  status int(2) DEFAULT 0,
  finishedGames int(6) DEFAULT 0,
  winUserId int(11) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY tourUID (tourUID),
  FOREIGN KEY (createUserId)
        REFERENCES user(id),
  FOREIGN KEY (winUserId)
        REFERENCES user(id)
);

/* when tourType=0, its a sologame and hence we map it to this table */

CREATE TABLE IF NOT EXISTS user_sologame (
  id int(11) NOT NULL AUTO_INCREMENT,
  userId int(11) NOT NULL,
  tourId int(11) NOT NULL,
  agentId varchar(64) NOT NULL,
  winCount int(6) DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY unique_user (userId,tourId),
  FOREIGN KEY (tourId)
        REFERENCES tournament(id)
        ON DELETE CASCADE,
  FOREIGN KEY (userId)
        REFERENCES user(id)
        ON DELETE CASCADE
);

/* when tourType!=0, its a tournament and hence we map it to this table */

CREATE TABLE IF NOT EXISTS user_tour (
  id int(11) NOT NULL AUTO_INCREMENT,
  userId int(11) NOT NULL,
  tourId int(11) NOT NULL,
  agentId varchar(64) NOT NULL, 
  PRIMARY KEY (id),
  UNIQUE KEY unique_user (userId,tourId),
  FOREIGN KEY (tourId)
        REFERENCES tournament(id)
        ON DELETE CASCADE,
  FOREIGN KEY (userId)
        REFERENCES user(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tourGame (
  id int(11) NOT NULL AUTO_INCREMENT,
  tourId int(11) NOT NULL,
  noPlayers int(2),
  createTime int(11) DEFAULT NULL,
  winnerIndex int(11) DEFAULT NULL,
  status int(2) DEFAULT 0,
  finishedGames int(6) DEFAULT 0,
  PRIMARY KEY (id),
  FOREIGN KEY (tourId)
        REFERENCES tournament(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_tourGame (
  id int(11) NOT NULL AUTO_INCREMENT,
  userId int(11) NOT NULL,
  gameId int(11) NOT NULL,
  agentId varchar(64) NOT NULL,
  winCount int(6) DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY unique_user (userId,gameId),
  FOREIGN KEY (gameId)
        REFERENCES tourGame(id)
        ON DELETE CASCADE,
  FOREIGN KEY (userId)
        REFERENCES user(id)
        ON DELETE CASCADE
);
