import sys
import string
import pymysql.cursors
from re import match
from copy import deepcopy
from functools import partial
from yaml import load,FullLoader
from random import SystemRandom,shuffle

from dice import Dice
from cards import Cards
from state import State, Phase
from constants import communityChestCards,chanceCards

from actions.mapper import Mapper
import actions.startGame
import actions.jailDecision
import actions.buyProperty
import actions.auctionProperty
import actions.mortgage
import actions.sellHouses
import actions.handleTrade
import actions.tradeResponse
import actions.buyHouses
import actions.endGame
import actions.receiveState

import actions.startTurn
import actions.diceRoll
import actions.cards
import actions.endTurn


# autobahn imports
from os import environ
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

"""CONFIGURATION SETTINGS"""
# will wait seconds represented by TIMEOUT for all players to join
TIMEOUT = 610

class Adjudicator(ApplicationSession):
    
    @inlineCallbacks
    def onJoin(self, details):
        #TODO: Configuration for these
        self.gameId = sys.argv[1]
        self.noPlayers = int(sys.argv[2])
        self.noGames = int(sys.argv[3])
        self.timePerMove = int(sys.argv[4])

        #self.gameId = 1
        #self.noPlayers = 2
        #self.noGames =1

        # load db details
        self.mysql_host = environ.get('MYSQL_HOST', 'localhost')
        with open("creds.yaml") as f:
            data = load(f,Loader=FullLoader)
            self.mysql_user = data['creds']['user']
            self.mysql_pass = str(data['creds']['password'])
        
        if self.mysql_user is None or self.mysql_pass is None:
            self.logger("Leaving early")
            self.leave()
        
        # the players who have joined the game
        # maps the sessionId to a dict containing email and no of wins
        self.agents = {}
        
        #TODO: Sync
        self.gameStarted = False

        self.endpoints = {
            'REQUEST'   : 'monopoly.game{}.agent{}.request',
            'RESPONSE'  : 'monopoly.game{}.agent{}.response'
        }
        
        self.agentDefaultOptions = {
            Phase.START_TURN         : False,
            Phase.JAIL_RESULT        : False,
            Phase.DICE_ROLL          : False,
            Phase.CHANCE_CARD        : False,
            Phase.COMMUNITY_CHEST    : False,
            Phase.AUCTION_RESULT     : False,
            Phase.MORTGAGE_RESULT    : False,
            Phase.UNMORTGAGE_RESULT  : False,
            Phase.SELL_HOUSES_RESULT : False,
            Phase.TRADE_RESULT       : False,
            Phase.BUY_HOUSES_RESULT  : False,
            Phase.END_TURN           : False
        }

        self.phaseToClass = {
            Phase.START_GAME         : {
                'publish'   : actions.startGame.publish,
                'subscribe' : actions.startGame.subscribe,
                'broadcast' : True
            },
            Phase.START_TURN         : {
                'publish'   : actions.startTurn.publish,
                'subscribe' : actions.startTurn.subscribe,
                'broadcast' : False
            },
            Phase.JAIL               : {
                'publish'   : actions.jailDecision.publish,
                'subscribe' : actions.jailDecision.subscribe,
                'broadcast' : False
            },
            Phase.BUY                : {
                'publish'   : actions.buyProperty.publish,
                'subscribe' : actions.buyProperty.subscribe,
                'broadcast' : False
            },
            Phase.AUCTION            : {
                'publish'   : actions.auctionProperty.publish,
                'subscribe' : actions.auctionProperty.subscribe,
                'broadcast' : True
            },
            Phase.MORTGAGE           : {
                'publish'   : actions.mortgage.publish,
                'subscribe' : actions.mortgage.subscribe,
                'broadcast' : False
            },
            Phase.UNMORTGAGE           : {
                'publish'   : actions.mortgage.publish,
                'subscribe' : actions.mortgage.subscribe,
                'broadcast' : False
            },
            Phase.SELL_HOUSES        : {
                'publish'   : actions.sellHouses.publish,
                'subscribe' : actions.sellHouses.subscribe,
                'broadcast' : False
            },
            Phase.TRADE              : {
                'publish'   : actions.handleTrade.publish,
                'subscribe' : actions.handleTrade.subscribe,
                'broadcast' : False
            },
            Phase.TRADE_RESPONSE     : {
                'publish'   : actions.tradeResponse.publish,
                'subscribe' : actions.tradeResponse.subscribe,
                'broadcast' : False
            },
            Phase.BUY_HOUSES         : {
                'publish'   : actions.buyHouses.publish,
                'subscribe' : actions.buyHouses.subscribe,
                'broadcast' : False
            },
            Phase.END_TURN           : {
                'publish'   : actions.endTurn.publish,
                'subscribe' : actions.endTurn.subscribe,
                'broadcast' : False
            },
            Phase.END_GAME           : {
                'publish'   : actions.endGame.publish,
                'subscribe' : actions.endGame.subscribe,
                'broadcast' : True
            },
            Phase.DICE_ROLL          : {
                'publish'   : actions.diceRoll.publish,
                'subscribe' : actions.diceRoll.subscribe,
                'broadcast' : False
            },
            Phase.CHANCE_CARD        : {
                'publish'   : actions.cards.publish,
                'subscribe' : actions.cards.subscribe,
                'broadcast' : False
            },
            Phase.COMMUNITY_CHEST    : {
                'publish'   : actions.cards.publish,
                'subscribe' : actions.cards.subscribe,
                'broadcast' : False
            },
            Phase.BUY_RESULT         : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.JAIL_RESULT        : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.AUCTION_RESULT     : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.MORTGAGE_RESULT    : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.UNMORTGAGE_RESULT  : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.SELL_HOUSES_RESULT : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.TRADE_RESULT       : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            },
            Phase.BUY_HOUSES_RESULT  : {
                'publish'   : actions.receiveState.publish,
                'subscribe' : actions.receiveState.subscribe,
                'broadcast' : True
            }
        }
        
        #determines the state to be used as initial state
        self.INITIAL_STATE = 'DEFAULT'
        # self.INITIAL_STATE = 'TEST_BUY_HOUSES'
        
        # after timeout, don't wait for new players anymore
        # if enough players haven't joined, either start the game or stop it
        self.timeoutId = reactor.callLater(TIMEOUT, self.timeoutHandler)
        
        yield self.register(self.joinGame,'com.game{}.joingame'.format(self.gameId))

        sql = "SELECT id FROM tournament WHERE tourUID=%s"
        res = self.singleQuery(sql,(self.gameId,))
        if 'id' not in res:
            self.logger("SQL fetch of tourId failed")
            self.leave()
        self.gameIndex = res['id']

    def logger(self,msg):
        print(msg)
        #with open("newAdjudicator_{}.log".format(self.gameId), "a") as f:
        #    f.write(msg+"\n")
        #pass

    def timeoutHandler(self):
        self.logger('In joingame timeoutHandler')
        if not self.gameStarted:
            sql = "DELETE FROM tournament WHERE tourUID=%s"
            payload = (self.gameId,)
            self.singleQuery(sql,payload,commit=True)
            
            self.leave()

    # called by agent to join this game.
    # argument is sessionId
    def joinGame(self,*args):
        ERROR = "Implementation error. Please contact admins."

        try:
            sessionId = args[0]
        except:
            return [1,"Please provide your current sessionId from the WebUI as argument while joining a game."]

        if not (isinstance(sessionId,str) and match('^[a-zA-Z0-9]+$',sessionId)):
            return [1,"The provided sessionId had an invalid format."]

        agentOptions = deepcopy(self.agentDefaultOptions)
        if len(args) > 1 and isinstance(args[1],dict):
            for key,value in args[1].items():
                if key in agentOptions:
                    agentOptions[key] = value

        sql = "SELECT id,email FROM user WHERE sessionId=%s"
        payload = (sessionId,)
        creds = self.singleQuery(sql,payload)
        if creds is None:
            return [1,"The given sessionId doesn't exist in the store. Please try refreshing the page to renew the session."]

        if creds['email'] in self.agents:
            # TODO: send him to the correct point in the game
            self.logger("Agent was already in the game")
            self.agents[creds['email']]['sessionId'] = sessionId
            return [0,creds['email']]
        elif len(self.agents) < self.noPlayers:
            if not self.addUser(self.gameId, creds['id']):
               self.logger("addUser SQL query failed")
               return [1,ERROR]

            self.agents[creds['email']] = {
                'id': creds['id'],
                'sessionId': sessionId,
                'agentOptions': agentOptions,
                'wins': 0,
                'subKeys': []
            }
            self.logger("{} agents have joinedout of {}".format(len(self.agents),self.noPlayers))
            if len(self.agents) == self.noPlayers:
                # start the game after 10 seconds, allow time for the newly joined agent
                reactor.callLater(10, self.startGame)
            
            self.logger("Player {} has joined the game.".format(creds['email']))
            return [0,creds['email']]
        
        # can't join anymore
        return [1,"The game is full. Sorry."]

    def singleQuery(self, sql, payload, commit=False):
        # SQL Connection
        connection = pymysql.connect(host=self.mysql_host,
                             port=3306,
                             user=self.mysql_user,
                             password=self.mysql_pass,
                             db='monopoly',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        res = None
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, payload)
                if not commit: res = cursor.fetchone()
            if commit: connection.commit()
        except:
            self.logger("SQL query failed.")
        finally:
            connection.close()

        return res

    def addUser(self, gameId, userId):
        res = True
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
                sql = "INSERT INTO user_sologame (userId,tourId) VALUES (%s,%s)"
                cursor.execute(sql, (userId,self.gameIndex))
            connection.commit()
        except Exception as e:
            self.logger("SQL SELECT/INSERT in addUser failed.")
            res = False
        finally:
            connection.close()

        return res
    
    @inlineCallbacks
    def uiUpdateChannel(self,args):
        if args['type'] == 0:
            # a game has completed
            sql = "UPDATE tournament SET finishedGames=%s WHERE tourUID=%s"
            payload = (self.gamesCompleted, self.gameId)
            self.singleQuery(sql,payload,commit=True)

            sql = "UPDATE user_sologame SET winCount=%s WHERE userId=%s AND tourId=%s"
            for winnerId in args['winners']:
                winner = self.agents[winnerId]
                payload = (winner['wins'],winner['id'],self.gameIndex)
                self.singleQuery(sql,payload,commit=True)

            winsCount = []
            for agent,info in self.agents.items():
                winsCount.append([agent,info['wins']])
            payload = [0,self.gameId,self.gamesCompleted,winsCount]
            yield self.publish('com.game{}.uiupdates'.format(self.gameId), payload)
        elif args['type'] == 1:
            # starting a game
            sql = "UPDATE tournament SET status=1 WHERE tourUID=%s"
            payload = (self.gameId,)
            self.singleQuery(sql,payload,commit=True)

            payload = [1,self.gameId]
            yield self.publish('com.game{}.uiupdates'.format(self.gameId), payload)
        elif args['type'] == 2:
            sql = "UPDATE tournament SET status=2 WHERE tourUID=%s"
            payload = (self.gameId,)
            self.singleQuery(sql,payload,commit=True)

            payload = [2,self.gameId]
            yield self.publish('com.game{}.uiupdates'.format(self.gameId), payload)
    
    def shutDown(self):
        for _,data in self.agents.items():
            for subKey in data['subKeys']:
                subKey.unsubscribe()

        self.uiUpdateChannel({'type':2})
        self.leave()
    
    # called after we call self.leave()
    def onDisconnect(self):
        self.logger("Disconnecting")
        if reactor.running:
            reactor.stop()
    
    #TODO: loop here using self.NO_OF_GAMES
    @inlineCallbacks
    def startGame(self):
        self.gameStarted = True
        if self.timeoutId.active():
            self.timeoutId.cancel()

        self.logger("Game started")
        self.uiUpdateChannel({'type':1})

        self.gamesCompleted = 0
        PLAY_ORDER = list(self.agents.keys())
        shuffle(PLAY_ORDER)
        
        self.winner = None
        self.dice = Dice()
        self.chest = Cards(communityChestCards)
        self.chance = Cards(chanceCards)
        self.state =  State(PLAY_ORDER,self.timePerMove)
        self.mortgagedDuringTrade = []

        # used during JailDecision
        self.diceThrown = False

        # used with Phase.BUY to decide which agent MORTGAGE & SELL_HOUSES
        # should be called for
        self.bsmAgentId = PLAY_ORDER[0]
        self.auctionStarted = False
        self.tradeCounter = 0

        self.mapper = Mapper(self)

        for agentId in PLAY_ORDER:
            sessionId = self.agents[agentId]['sessionId']
            uri = self.endpoints['RESPONSE'].format(self.gameId, sessionId)
            sub = yield self.subscribe(partial(self.mapper.response,sessionId), uri)
            self.agents[agentId]['subKeys'].append(sub)

        self.mapper.request()
    
if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit("Not enough arguments")
    import six
    url = environ.get("CBURL", u"ws://127.0.0.1:4000/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(Adjudicator)
