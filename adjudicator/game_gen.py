import sys
from yaml import load,FullLoader
from os import environ
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from subprocess import Popen,PIPE
import pymysql.cursors
import string
from time import time,sleep
from random import SystemRandom
from re import match
from math import floor

from google.oauth2 import id_token
from google.auth.transport import requests

GAMEID_LENGTH = 16
SESSIONID_LENGTH = 16
GAME_EXPIRE_TIME = 600

class GameGen(ApplicationSession):
    
    @inlineCallbacks
    def onJoin(self, details):
        self.logger("In "+self.onJoin.__name__)

        # load db details
        self.mysql_host = environ.get('MYSQL_HOST', 'localhost')
        with open("creds.yaml") as f:
            data = load(f,Loader=FullLoader)
            self.mysql_user = data['creds']['user']
            self.mysql_pass = str(data['creds']['password'])
        
        if self.mysql_user is None or self.mysql_pass is None:
            self.logger("Leaving early")
            self.leave()
        
        self.gameid_counter = 0
        self.games_list = []

        self.confirm_registration_handles = {}
        
        #called by the Start New Game UI
        yield self.register(self.signin,"com.monopoly.signin")
        yield self.register(self.signout,"com.monopoly.signout")
        yield self.register(self.create_game,"com.monopoly.create_game")
        yield self.register(self.fetch_games,"com.monopoly.fetch_games")
        yield self.register(self.addOurAgent,"com.monopoly.add_our_agent")

    def logger(self,msg):
        #print(msg)
        with open("game_gen.log", "a") as f:
            f.write(msg+"\n")
        #pass


    def signin(self,*args):
        self.logger("Inside signin")
        ERROR = "ERROR"

        try:
            email = args[0]
            user_token = args[1]
        except:
            return ERROR

        # Specify the Google Client ID here
        # More info can be found here:
        # https://developers.google.com/identity/sign-in/web/sign-in
        CLIENT_ID = '';
        try:
            idinfo = id_token.verify_oauth2_token(user_token, requests.Request(), CLIENT_ID)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            authEmail = idinfo['email']
            self.logger("Email: "+authEmail)

            if email != authEmail:
                # Successfully authenticated
                return ERROR

        except ValueError:
            # Invalid token
            self.logger("Invalid Token")
            return ERROR

        session_id = ''.join(SystemRandom().choice(string.ascii_letters +
            string.digits) for _ in range(SESSIONID_LENGTH))

        connection = pymysql.connect(host=self.mysql_host,
                             port=3306,
                             user=self.mysql_user,
                             password=self.mysql_pass,
                             db='monopoly',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        result = None
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT `email` FROM `user` WHERE `email`=%s"
                cursor.execute(sql, (email,))
                result = cursor.fetchone()
        except:
            self.logger("SQL SELECT in signin failed.")
            connection.close()
            return ERROR

        if result is None:
            sql = "INSERT INTO `user` (`email`,`sessionId`,`lastActivity`) VALUES (%s,%s,%s)"
            data = (email, session_id, time())
        else:
            sql = "UPDATE `user` SET `sessionId`=%s, `lastActivity`=%s WHERE `email`=%s"
            data = (session_id, time(), email)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
            connection.commit()
        except:
            self.logger("SQL user table updation command failed.")
            return ERROR
        finally:
            connection.close()

        return session_id

    def signout(self,*args):
        self.logger("Inside signout")

        try:
            email = args[0]
        except:
            return False

        connection = pymysql.connect(host=self.mysql_host,
                             port=3306,
                             user=self.mysql_user,
                             password=self.mysql_pass,
                             db='monopoly',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE `user` SET `sessionId`=%s, `lastActivity`=%s WHERE `email`=%s"
                cursor.execute(sql, (None, None, email))

            connection.commit()
        except:
            self.logger("SQL UPDATE failed.")
            return False
        finally:
            connection.close()

        return True

    def create_game(self,*args):
        self.logger("Inside create_game")
        ERROR = "Implementation error. Please contact admins."

        try:
            sessionId = args[0]
            gameType = int(args[1])
            noPlayers = int(args[2])
            noGames = int(args[3])
            timePerMove = int(args[4])
            allowHumans = bool(args[5])
            if gameType > 0:
                noPpg = 2
                if len(args) > 4:
                    noPpg = int(args[6])
            else:
                noPpg = None
                    
        except:
            return [1,"Insufficient number of parameters. Please include session ID, game type, number of players and number of games."]

        if not (isinstance(sessionId,str) and match('^[a-zA-Z0-9]+$',sessionId)):
            return [1,"Invalid session ID."]

        if gameType < 0 or gameType > 2:
            return [1,"Invalid value for game type"]

        if noPlayers < 2:
            return [1,"Number of players should be greater than 2"]

        if gameType == 0 and noPlayers > 8:
            return [1,"Number of players should be less than 8"]

        if noGames < 1:
            return [1,"Invalid value for number of games"]

        if timePerMove < 3:
            return [1,"A time per move < 3 would face network latency issues. Please try again."]
    
        if gameType > 0 and (noPpg < 2 or noPpg > 8):
            return [1,"Invalid value for number of players per game"]  
        
        connection = pymysql.connect(host=self.mysql_host,
                             port=3306,
                             user=self.mysql_user,
                             password=self.mysql_pass,
                             db='monopoly',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        # get a unique tourUID
        tourUID = ''.join(SystemRandom().choice(string.ascii_letters +
            string.digits) for _ in range(GAMEID_LENGTH))
        
        searchSQL = "SELECT tourUID FROM tournament WHERE tourUID=%s"

        while True:
            try:
                with connection.cursor() as cursor:
                    # Create a new record
                    cursor.execute(searchSQL,(tourUID,))
                    result = cursor.fetchone()
                    if result is None:
                        # the tourUID is not in the table
                        break
                    
                    tourUID = ''.join(SystemRandom().choice(string.ascii_letters +
                        string.digits) for _ in range(GAMEID_LENGTH))
                    self.logger("There was an ID collision")
            except:
                self.logger("SQL SELECT in create_game failed.")
                connection.close()
                return [1,ERROR]

        userId = self.fetch_creds(sessionId, connection)
        if userId is None:
            # Possibly indicating session timeout
            connection.close()
            return [1,"Invalid session ID."]
        
        createSQL = """INSERT INTO tournament (tourUID, tourType, noPlayers,
            noGames, noPpg, createUserId, createTime, timePerMove, allowHumans)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        createPayload = (tourUID, gameType, noPlayers, noGames, noPpg,
                userId['id'], time(), timePerMove, allowHumans)

        try:
            with connection.cursor() as cursor:
                # Create a new record
                cursor.execute(createSQL, createPayload)
            connection.commit()
        except:
            self.logger("SQL INSERT failed.")
            tourUID = "ERROR"
        finally:
            connection.close()

        if tourUID == "ERROR":
            return [1,ERROR]
        
        # sys.executable gets the python executable used to start the current script
        if gameType == 0:
            popen_id = Popen([sys.executable,"./newAdjudicator.py",str(tourUID),
                str(noPlayers),str(noGames),str(timePerMove)])
            sleep(2)

        self.logger("Generated tourUID: "+tourUID)
        return [0,tourUID]

    def fetch_creds(self, sessionId, connection):
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT id,email FROM user WHERE sessionId=%s"
                cursor.execute(sql, (sessionId,))
                result = cursor.fetchone()
                return result
        except:
            self.logger("SQL SELECT in signin failed.")
            return None

    def fetch_games(self,*args):
        self.logger("Inside fetch_games")

        try:
            sessionId = args[0]
            requestType = args[1]

            if requestType == 0:
                # fetch a single game
                tourUID = args[2]
            else:
                # fetch all games the current user created or has joined
                fetchNew = args[2]
        except:
            return []

        if not (isinstance(sessionId,str) and match('^[a-zA-Z0-9]+$',sessionId)):
            return []
        
        # SQL Connection
        connection = pymysql.connect(host=self.mysql_host,
                             port=3306,
                             user=self.mysql_user,
                             password=self.mysql_pass,
                             db='monopoly',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        
        creds = self.fetch_creds(sessionId, connection)
        if creds is None:
            return []

        if requestType == 0:
            if not (isinstance(tourUID,str) and match('^[a-zA-Z0-9]+$',tourUID)):
                return []
            # fetch a single game using the unique tourUID
            result = self.fetch_tournament(tourUID,creds['email'],connection)
        else:
            result = self.fetch_mygames(fetchNew,creds['id'],creds['email'],connection)

        connection.close()        
        return result

    # fetches the tournament with the given id
    # if not found, returns None
    def fetch_tournament(self,tourId, email, connection):
        self.logger("In fetch_tournament for {}".format(tourId))
        fetchSql = """SELECT id, tourUID, tourType, noPlayers, noGames, noPpg,
                    createTime, createUserId, timePerMove, allowHumans, status,
                    finishedGames, winUserId
                    FROM tournament WHERE tourUID=%s;"""
        result = None
        try:
            with connection.cursor() as cursor:
                cursor.execute(fetchSql, (tourId,))
                resSet = cursor.fetchone()
                if resSet is None:
                    return []

                uSql = "SELECT email FROM user WHERE id=%s"
                cursor.execute(uSql, (resSet['createUserId'],))
                cResSet = cursor.fetchone()
                if cResSet is None:
                    return []
                
                expireTime = floor(resSet['createTime'] + GAME_EXPIRE_TIME - time())

                if resSet['tourType'] == 0:
                    jSql = """SELECT u.email,ug.winCount
                            FROM user u JOIN user_sologame ug
                            ON u.id = ug.userId WHERE ug.tourId=%s"""
                else:
                    jSql = """SELECT u.email
                            FROM user u JOIN user_tour ug
                            ON u.id = ug.userId WHERE ug.tourId=%s"""

                cursor.execute(jSql, (resSet['id'],))
                userSet = cursor.fetchall()

                jPlayers = []
                if userSet is not None:
                    for user in userSet:
                        if 'winCount' in user:
                            jPlayers.append([user['email'],user['winCount']])
                        else:
                            jPlayers.append([user['email']])

                result = {
                    'tourId'       : resSet['tourUID'],
                    'tourType'     : resSet['tourType'],
                    'noPlayers'    : resSet['noPlayers'],
                    'noGames'      : resSet['noGames'],
                    'expireTime'   : expireTime,
                    'jPlayers'     : jPlayers,
                    'creator'      : cResSet['email'],
                    'status'       : resSet['status'],
                    'finishedGames': resSet['finishedGames'],
                    'timePerMove'  : resSet['timePerMove'],
                    'allowHumans'  : resSet['allowHumans']
                }
                if resSet['tourType'] > 0:
                    result['noPpg'] = resSet['noPpg']

                if resSet['winUserId'] is not None:
                    cursor.execute(uSql, (resSet['winUserId'],))
                    cResSet = cursor.fetchone()
                    if cResSet is not None:
                        result['winner'] = cResSet['email']

        except Exception as e:
            self.logger("SQL SELECT inside fetch_tournament failed.")
            result = None

        if result is None:
            self.logger("Result was None")
            return []
        
        return [result]

    def processTour(self,sql,args,cursor,email):
        cursor.execute(sql, args)
        resSets = cursor.fetchmany(size=25)

        if resSets is None:
            return []

        result = []
        for resSet in resSets:
            expireTime = floor(resSet['createTime'] + GAME_EXPIRE_TIME - time())

            self.logger("Fetching joined Players using tourId: "+str(resSet['id']))
            jSQL = """SELECT u.email,ug.winCount FROM user u
                    JOIN user_sologame ug ON u.id = ug.userId
                    WHERE ug.tourId=%s"""
            cursor.execute(jSQL, (resSet['id'],))
            userSet = cursor.fetchall()

            jPlayers = []
            if userSet is not None:
                for user in userSet:
                    jPlayers.append([user['email'],user['winCount']])

            record = {
                'tourId'       : resSet['tourUID'],
                'tourType'     : resSet['tourType'],
                'noPlayers'    : resSet['noPlayers'],
                'noGames'      : resSet['noGames'],
                'expireTime'   : expireTime,
                'jPlayers'     : jPlayers,
                'status'       : resSet['status'],
                'finishedGames': resSet['finishedGames']
            }
            if resSet['tourType'] == 0:
                    record['noPpg'] = resSet['noPpg']

            if resSet['winUserId'] is not None:
                uSql = "SELECT email FROM user WHERE id=%s"
                cursor.execute(uSql, (resSet['winUserId'],))
                cResSet = cursor.fetchone()
                if cResSet is not None:
                    record['winner'] = cResSet['email']

            result.append(record)

        return result

    # fetches the games which the user created or has joined
    # if found, returns a list with the game as single element
    # if not found, returns an empty list
    def fetch_mygames(self,fetchNew,userId,email,connection):
        if fetchNew:
            whereClause = "(status=0 and UNIX_TIMESTAMP(CURRENT_TIMESTAMP) - createTime <= {}) OR status=1".format(GAME_EXPIRE_TIME)
        else:
            whereClause = "status=2"

        creatorSql = """SELECT id, tourUID, tourType, noPlayers, noGames,
                    noPpg, createTime, status, finishedGames, winUserId
                    FROM tournament WHERE createUserId=%s AND {}
                    ORDER BY createTime DESC;""".format(whereClause)
        joineeSQL = """SELECT t.id, t.tourUID, t.tourType, t.noPlayers,
                    t.noGames, t.noPpg, t.createTime, t.status,
                    t.finishedGames, t.winUserId
                    FROM tournament t JOIN user_sologame ug ON t.id=ug.tourId
                    AND ug.userId=%s WHERE {}
                    ORDER BY t.createTime DESC;""".format(whereClause)
        result = []
        try:
            with connection.cursor() as cursor:
                # games current user has created
                cRecords = self.processTour(creatorSql,(userId,),cursor,email)

                # games where current user has joined
                jRecords = self.processTour(joineeSQL,(userId,),cursor,email)

                result = [cRecords, jRecords]

        except Exception as e:
            self.logger("SQL SELECT inside fetch_mygames failed.")
            self.logger(str(e))
            result = []

        return result
    
    def addOurAgent(self,*args):
        self.logger("Inside addOurAgent with args: "+str(args))
        # TODO
        pass
            
        
    def onDisconnect(self):
        if reactor.running:
            reactor.stop()

if __name__ == '__main__':
    import six
    url = environ.get("CBURL", u"ws://127.0.0.1:4000/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(GameGen)
