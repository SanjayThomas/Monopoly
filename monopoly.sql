SET GLOBAL event_scheduler = ON;

USE mysql;
CREATE USER 'root'@'%' IDENTIFIED BY 'root123';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

DROP DATABASE IF EXISTS monopoly;
CREATE DATABASE monopoly;

USE monopoly;

CREATE TABLE IF NOT EXISTS user (
  id int NOT NULL AUTO_INCREMENT,
  email varchar(255),
  sessionId varchar(32) DEFAULT NULL,
  lastActivity int DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email (email),
  UNIQUE KEY sessionId (sessionId)
);

CREATE EVENT remove_old_sessions
ON SCHEDULE EVERY 3 MINUTE
DO UPDATE user SET sessionId=NULL, lastActivity=NULL WHERE UNIX_TIMESTAMP(CURRENT_TIMESTAMP) - lastActivity > 1800;

/* status: 0=not started, 1=started, 2=finished */

CREATE TABLE IF NOT EXISTS tournament (
  id int NOT NULL AUTO_INCREMENT,
  tourUID varchar(32) NOT NULL,
  tourType tinyint DEFAULT 0,
  noPlayers smallint DEFAULT 2,
  noGames smallint DEFAULT 100,
  noPpg tinyint DEFAULT NULL,
  createUserId int NOT NULL,
  createTime int NOT NULL,
  timePerMove smallint DEFAULT 5,
  allowHumans tinyint DEFAULT 0,
  status tinyint DEFAULT 0,
  finishedGames smallint DEFAULT 0,
  winUserId int DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY tourUID (tourUID),
  FOREIGN KEY (createUserId)
        REFERENCES user(id),
  FOREIGN KEY (winUserId)
        REFERENCES user(id)
);

/* when tourType=0, its a sologame and hence we map it to this table */

CREATE TABLE IF NOT EXISTS user_sologame (
  id int NOT NULL AUTO_INCREMENT,
  userId int NOT NULL,
  tourId int NOT NULL,
  winCount smallint DEFAULT 0,
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
  id int NOT NULL AUTO_INCREMENT,
  userId int NOT NULL,
  tourId int NOT NULL,
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
  id int NOT NULL AUTO_INCREMENT,
  tourId int NOT NULL,
  noPlayers smallint,
  createTime int DEFAULT NULL,
  winUserId int DEFAULT NULL,
  status tinyint DEFAULT 0,
  finishedGames smallint DEFAULT 0,
  PRIMARY KEY (id),
  FOREIGN KEY (tourId)
        REFERENCES tournament(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_tourGame (
  id int NOT NULL AUTO_INCREMENT,
  userId int NOT NULL,
  gameId int NOT NULL,
  winCount smallint DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY unique_user (userId,gameId),
  FOREIGN KEY (gameId)
        REFERENCES tourGame(id)
        ON DELETE CASCADE,
  FOREIGN KEY (userId)
        REFERENCES user(id)
        ON DELETE CASCADE
);
