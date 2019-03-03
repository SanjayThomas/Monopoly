import sys
from os import environ
from board import Type, Group
from state import State

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class Component(ApplicationSession):
    """
    An application component calling the different backend procedures.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("Session attached!")
        
        #TODO: Configuration for these
        #Command line args
        self.game_id = int(sys.argv[1])
        
        #URIs
        join_game_uri = 'com.game{}.joingame'.format(self.game_id)
        
        # call a remote procedure.
        res = yield self.call(join_game_uri)
        print("The agent was assigned id: {}".format(res['agent_id']))
        
        self.id = res['agent_id']
        self.pid = self.id
        self.minMoney = 200
        self.stealing = False
        
        self.register(self.getBSMTDecision,res['bsm'])
        self.register(self.respondTrade,res['respondtrade'])
        self.register(self.buyProperty,res['buy'])
        self.register(self.auctionProperty,res['auction'])
        self.register(self.jailDecision,res['jail'])
        self.register(self.receiveState,res['receivestate'])
        self.register(self.getTradeDecision,res['trade'])
        
        # subsribe for end game results
        yield self.subscribe(self.endGame,res["endgame"])

        #Successfully Registered. Invoke confirm_register
        res = yield self.call(res['confirm_register'])
        print("Result of calling confirm_register: "+str(res))


    def onDisconnect(self):
        print("disconnected")
        if reactor.running:
            reactor.stop()

    def endGame(self):
        # do some cleanup stuff if you have any
        self.leave()

    def getBSMTDecision(self, state):
        state = State(state)
        if state.money[self.pid] - state.debt[self.pid].getTotalDebt() < 0:
            pos = state.positions[self.pid]
            prop = state.properties[pos]
            if pos == -1 or not (prop.data.price == state.debt[self.pid * 2 + 1] and prop.owner == -1):
                return self.getBestActionForMoney(state)
        if state.money[self.pid] < self.getSafeMoney(state):
            return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
        bestGroup = self.getBestGroupToImprove(state)
        if bestGroup:
            groupProps = state.getGroupProperties(bestGroup)
            cost = len(groupProps) * groupProps[0].data.houseCost
            if state.money[self.pid] < self.getSafeMoney(state) + cost:
                return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
            for prop in groupProps:
                if prop.mortgaged:
                    return "M", [prop.id]
            return "B", [(prop.id, 1) for prop in groupProps]
        return None

    def respondTrade(self, state):
        return False

    def buyProperty(self, state):
        state = State(state)
        prop = state.properties[state.phaseData]
        opponents = state.getOpponents(self.pid)
        bestGroup = self.getBestGroupToImprove(state)
        if bestGroup: return False
        self.stealing = True
        for opponent in opponents:
            if state.money[opponent] >= prop.data.price:
                self.stealing = False
        if self.stealing: return False
        return True

    def auctionProperty(self, state):
        state = State(state)
        data = None 
        if type(state.phaseData) is int:
            data = state.phaseData
        else:
            data = state.phaseData[0] 
        prop = state.properties[data]
        opponents = state.getOpponents(self.pid)
        bid = prop.data.price // 2 + 1
        if self.stealing:
            bid = prop.data.price
            self.stealing = False
        maxOpponent = 0
        for opponent in opponents:
            if state.money[opponent] > maxOpponent:
                maxOpponent = state.money[opponent]
        if maxOpponent < bid: bid = maxOpponent
        return min(state.money[self.pid], bid)

    def jailDecision(self, state):
        state = State(state)
        if self.getSafeMoney(state) > self.minMoney:
            return "R"
        else:
            return "P"

    def receiveState(self, state):
        pass

    def getTradeDecision(self,state):
        return None

    def getExpectedRent(self, prop, houses, turn):
        data = prop.data
        opponentTurnsLeft = (100 - turn) / 2
        return data.rents[houses] * data.probability * opponentTurnsLeft

    def getSafeMoney(self, state):
        maxRent = 0
        for prop in state.properties:
            if (prop.owned and prop.owner == self.pid) or prop.id >= 40: continue
            rent = 0
            if prop.data.type == Type.PROPERTY:
                rent = prop.data.rents[prop.houses]
            if prop.data.type == Type.RAILROAD:
                rent = 25 * 2 ** 2
            if rent > maxRent: maxRent = rent
        return self.minMoney

    def getBestGroupToImprove(self, state):
        ownedGroups = state.getOwnedBuildableGroups(self.pid)
        maxRoi = 0
        bestGroup = None
        bestGroups = [Group.ORANGE, Group.LIGHT_BLUE, Group.RED, Group.PINK, Group.DARK_BLUE, Group.YELLOW, Group.GREEN, Group.BROWN]
        for group in bestGroups:
            if state.playerOwnsGroup(self.pid, group):
                groupProps = state.getGroupProperties(group)
                if groupProps[0].houses < 5: return group
        # for group in ownedGroups:
        #     props = state.getGroupProperties(group)
        #     if props[0].houses == 5: continue
        #     rent = sum([self.getExpectedRent(prop, prop.houses, state.turn) for prop in props])
        #     improvedRent = sum([self.getExpectedRent(prop, prop.houses + 1, state.turn) for prop in props])
        #     cost = len(props) * props[0].data.houseCost
        #     roi = (improvedRent - rent) / cost
        #     if roi > maxRoi:
        #         maxRoi = roi
        #         bestGroup = group
        return bestGroup

    def getBestMortgageAction(self, state, ignoredProps):
        props = state.getOwnedProperties(self.pid)
        maxRatio = 0
        bestProp = None
        for prop in props:
            if not prop.mortgaged and prop not in ignoredProps and prop.houses == 0:
                rent = 1
                if prop.data.type == Type.PROPERTY:
                    rent = prop.data.rents[prop.houses]
                if prop.data.type == Type.RAILROAD:
                    rent = 25 * 2 ** state.getRailroadCount((self.pid + 1) % 2)
                ratio = (prop.data.price // 2) / rent
                if ratio > maxRatio:
                    maxRatio = ratio
                    bestProp = prop
        if bestProp: return "M", [bestProp.id]
        return None

    def getBestActionForMoney(self, state):
        mortgageAction = self.getBestMortgageAction(state, [])
        if mortgageAction: return mortgageAction
        ownedGroups = state.getOwnedBuildableGroups(self.pid)
        for group in ownedGroups:
            groupProps = state.getGroupProperties(group)
            if groupProps[0].houses > 0:
                return "S", [(prop.id, 1) for prop in groupProps]

if __name__ == '__main__':
    import six
    url = environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = u"crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)