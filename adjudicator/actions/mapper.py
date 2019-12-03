from state import Phase, ACTION_TIMEOUT
from actions.constants import DEFAULT_ACTIONS
from twisted.internet import reactor

class Mapper:
	def __init__(self,context):
		self.context = context
		self.timeoutId = None
	
	def request(self):
		if (self.timeoutId is not None) and self.timeoutId.active():
			print("Timeout still active when starting request")
			self.timeoutId.cancel()

		context = self.context
		self.currentPhase = context.state.getPhase()
		self.responses = {}

		phaseToClass = self.context.phaseToClass
		
		# make any state updates required for current phase
		# activeAgents = call self.publish() for these agents
		activeAgents = context.phaseToClass[self.currentPhase]['publish'](context)

		# how many agents should we wait for in response()?
		isBroadcast = phaseToClass[self.currentPhase]['broadcast']
		if isBroadcast:
			if (self.currentPhase == Phase.START_GAME) or (self.currentPhase == Phase.END_GAME):
				self.agentsYetToRespond = list(context.state.players)
			else:
				self.agentsYetToRespond = list(context.state.getLivePlayers())
		else:
			if (self.currentPhase == Phase.BUY_HOUSES) or (self.currentPhase == Phase.SELL_HOUSES) or (self.currentPhase == Phase.MORTGAGE) or (self.currentPhase == Phase.UNMORTGAGE) or (self.currentPhase == Phase.TRADE):
				self.agentsYetToRespond = [context.bsmAgentId]
			elif (self.currentPhase == Phase.TRADE_RESPONSE):
				self.agentsYetToRespond = [context.tradeReceiver]
			else:
				self.agentsYetToRespond = [context.state.currentPlayerId]

		# don't need to contact these agents during this phase
		inactiveAgents = list(set(self.agentsYetToRespond) - set(activeAgents))

		for inactiveAgent in inactiveAgents:
			# if response is None, default action will be used in response()
			self.response(inactiveAgent, self.currentPhase, None)

		if len(activeAgents) > 0:
			self.timeoutId = reactor.callLater(ACTION_TIMEOUT, self.timeoutHandler)
		
		for activeAgent in activeAgents:
			uri = self.context.endpoints['REQUEST'].format(self.context.gameId, activeAgent)
			
			# making publish API call
			self.context.publish(uri, self.context.state.toJson())


	# if there is an error, use default action and proceed
	def response(self,*args):
		try:
			agentId = args[0]
			phase = args[1]
		except:
			return

		try:
			res = args[2]
		except:
			res = None

		if (phase == self.currentPhase) and agentId in self.agentsYetToRespond:
			self.agentsYetToRespond.remove(agentId)

			if res is None:
				# use default action
				res = DEFAULT_ACTIONS.get(phase, None)

			# record the response of the agent
			self.responses[agentId] = res

			if len(self.agentsYetToRespond)==0:
				#no more agents left to respond. The timeoutHandler is not required any longer.
				if (self.timeoutId is not None) and self.timeoutId.active():
					self.timeoutId.cancel()

				phaseToClass = self.context.phaseToClass
				nextPhase = phaseToClass[self.currentPhase]['subscribe'](self.context, self.responses)
				if nextPhase is None:
					print("Next phase is None for phase: {}".format(self.currentPhase))
					print("Shutting down the adjudicator instance.")
					self.context.shutDown()
				else:
					self.context.state.setPhase(nextPhase)
					self.request()

	def timeoutHandler(self):
		# The timeout handler doesn't need to be invoked again for the current action
		print("Timeout handler invoked for phase: {}".format(self.currentPhase))
		if self.timeoutId.active():
			self.timeoutId.cancel()
		for agentId in self.agentsYetToRespond:
			# These agents have timed out. Use default actions for them.
			print("Agent {} has timed out in phase {}".format(agentId,self.currentPhase))

			# use default action
			defaultAction = DEFAULT_ACTIONS.get(self.currentPhase, None)

			self.responses[agentId] = defaultAction

		phaseToClass = self.context.phaseToClass
		nextPhase = phaseToClass[self.currentPhase]['subscribe'](self.context, self.responses)
		self.context.state.setPhase(nextPhase)
		
		self.request()
