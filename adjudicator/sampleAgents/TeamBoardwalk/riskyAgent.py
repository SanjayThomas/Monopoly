import sys
from os import environ
from board import Type, Group
from state import State
from baseAgent import BaseAgent

import six
from autobahn.twisted.wamp import ApplicationRunner

class RiskyAgent(BaseAgent):
	def startGame(self,state):
		print("Inside startGame")
		self.pid = self.id
		self.minMoney = 200
		self.stealing = False
		return None
	
	def mortgage(self,state):
		state = State(state)
		print("Inside mortgage Listener")
		if state.money[self.pid] < 0:
			return self.getBestMortgageAction(state, [])
		if state.money[self.pid] < self.getSafeMoney(state):
			return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup:
			groupProps = state.getGroupProperties(bestGroup)
			cost = len(groupProps) * groupProps[0].data.houseCost
			if state.money[self.pid] < self.getSafeMoney(state) + cost:
				return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
		return None

	def unmortgage(self, state):
		state = State(state)
		print("Inside unmortgage Listener")
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup:
			groupProps = state.getGroupProperties(bestGroup)
			for prop in groupProps:
				if prop.mortgaged:
					return [prop.id]
		return None
	
	def sellHouses(self,state):
		state = State(state)
		print("Inside sellHouses Listener")
		if state.money[self.pid] < 0:
			return self.getBestSellingAction(state)
		return None
	
	def buyHouses(self,state):
		state = State(state)
		print("Inside buyHouses Listener")
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup:
			groupProps = state.getGroupProperties(bestGroup)
			cost = len(groupProps) * groupProps[0].data.houseCost
			if state.money[self.pid] < self.getSafeMoney(state) + cost:
				return [(prop.id, 1) for prop in groupProps]
		return None

	def respondTrade(self, state):
		return True

	def buyProperty(self, state):
		state = State(state)
		prop = state.properties[state.phaseData]
		print("Inside buyListener for {} with prop id: {}".format(self.pid,state.phaseData))
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
		print("Inside auctionListener for {} with prop id: {}".format(self.pid,state.phaseData))
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

	def getTradeDecision(self,state):
		state = State(state)
		# propose trade which completes a monopoly for current agent
		my_groups = []

		for group in range(0,8):
			my_count = 0
			opp_id = None
			opp_prop = None
			props = state.getGroupProperties(group)
			for prop in props:
				if prop.owner == self.pid:
					my_count+=1
				elif prop.owner is not None:
					opp_id = prop.owner
					opp_prop = prop.id

			if (my_count == len(props) - 1) and (opp_id is not None):
				print("Going to propose trade to {}".format(opp_id))
				if state.money[self.pid] > 100:
					cashOffer = 100
				else:
					cashOffer = state.money[self.pid]
				
				propOffer = []
				for uGroup in range(8,10):
					breakCondition = False
					uProps = state.getGroupProperties(uGroup)
					for uProp in uProps:
						if uProp.owner == self.pid:
							propOffer = [uProp.id]
							breakCondition = True
							break
					if breakCondition:
						break
				print("Prop offered: {}".format(propOffer))
				return [opp_id,cashOffer,propOffer,10,[opp_prop]]

		return None
	  
	def endGame(self,state):
		state = State(state)
		if isinstance(state.phaseData, dict):
			print("Total Stats:")
			print(state.phaseData)
		else:
			if len(state.phaseData) == 1:
				print("************* The winner is player {} *************".format(state.phaseData[0]))
			else:
				print("************* The winners are {} *************".format(state.phaseData))

	def getExpectedRent(self, prop, houses, turn):
		data = prop.data
		opponentTurnsLeft = (100 - turn) / 2
		return data.rents[houses] * data.probability * opponentTurnsLeft

	def getSafeMoney(self, state):
		maxRent = 0
		for prop in state.properties:
			if (prop.owner == self.pid) or prop.id >= 40: continue
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
		#	 props = state.getGroupProperties(group)
		#	 if props[0].houses == 5: continue
		#	 rent = sum([self.getExpectedRent(prop, prop.houses, state.turn) for prop in props])
		#	 improvedRent = sum([self.getExpectedRent(prop, prop.houses + 1, state.turn) for prop in props])
		#	 cost = len(props) * props[0].data.houseCost
		#	 roi = (improvedRent - rent) / cost
		#	 if roi > maxRoi:
		#		 maxRoi = roi
		#		 bestGroup = group
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
					railroadCount = 0
					for opponent in state.getOpponents(self.pid):
						railroadCount += state.getRailroadCount(opponent)
					rent = 25 * 2 ** railroadCount
				ratio = (prop.data.price // 2) / rent
				if ratio > maxRatio:
					maxRatio = ratio
					bestProp = prop
		if bestProp: return [bestProp.id]
		return None

	def getBestSellingAction(self, state):
		ownedGroups = state.getOwnedBuildableGroups(self.pid)
		for group in ownedGroups:
			groupProps = state.getGroupProperties(group)
			if groupProps[0].houses > 0:
				return [(prop.id, 1, False) for prop in groupProps]

if __name__ == '__main__':
	if len(sys.argv) < 3:
		sys.exit("Not enough arguments")
	
	url = environ.get("CBURL", u"ws://localhost:4000/ws")
	#url = environ.get("CBURL", u"ws://localhost/ws")
	if six.PY2 and type(url) == six.binary_type:
		url = url.decode('utf8')
	realm = environ.get('CBREALM', u'realm1')
	runner = ApplicationRunner(url, realm)
	runner.run(RiskyAgent)
