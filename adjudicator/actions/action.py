import six
import abc
from functools import partial
from twisted.internet import reactor

import constants
from dice import Dice
from state import State
from cards import Cards
from utils import replace_last

@six.add_metaclass(abc.ABCMeta)
class Action:
	
	def __init__(self):
		pass
	
	def setContext(self,context):
		self.context = context
		self.context.currentClass = self.__class__.__name__
		
		self.dice = context.dice
		self.chest = context.chest
		self.chance = context.chance
		self.state = context.state
		self.mortgagedDuringTrade = context.mortgagedDuringTrade
		self.winner = context.winner
		self.validSubs = 0
		
	def isOption(self,agentId,option):
		if agentId == None:
			agent_options = self.context.agent_default_options
		else:
			agent_options = self.context.agent_options[agentId]
			if agent_options == None:
				agent_options = self.context.agent_default_options
		return agent_options[option]
	
	def publishAction(self,agentId,actionClass):
		self.timeoutId = reactor.callLater(self.ACTION_TIMEOUT, partial(self.timeoutHandler,actionClass))
		agent_attributes = self.context.genAgentChannels(agentId,requiredChannel = actionClass)
		self.context.publish(agent_attributes[actionClass], self.state.toJson())
	
	def timeoutHandler(self,actionClass):
		#The timeout handler doesn't need to be invoked again for the current action
		if self.timeoutId.active():
			self.timeoutId.cancel()
		for agentId in self.agentsYetToRespond:
			#These agents have timed out. Use default actions for them.
			#TODO: Lock subscribe so that these agents can't invoke it in between
			print("Agent "+str(agentId)+" has timed out in class "+str(actionClass))
			default_action = self.DEFAULT_ACTIONS[actionClass]
			actionClass = replace_last(actionClass,"_IN","_OUT")
			agent_attributes = self.context.genAgentChannels(agentId,requiredChannel = actionClass)
			self.context.subscribe(agent_attributes[actionClass],default_action)
	
	def canAccessSubscribe(self,agentId):
		"""
		Check if the agent can access the current subscribe method at the time of invocation
		The game might have progressed to another ActionClass or another Player's turn.
		"""
		if agentId is None:
			return False
		
		if agentId in self.agentsYetToRespond and self.context.currentClass == self.__class__.__name__:
			# we are expecting this agent to respond to this action
			# indicate that the agent has responded to this action
			self.validSubs += 1
			self.agentsYetToRespond.remove(agentId)
			if len(self.agentsYetToRespond)==0:
				#no more agents left to respond. The timeoutHandler is not required any longer.
				if self.timeoutId.active():
					self.timeoutId.cancel()
			return True
		else:
			print("Agent "+str(agentId)+" can't access the subscribe of "+self.__class__.__name__+" in "+str(self.context.currentClass))
			return False

	@abc.abstractmethod
	def publish(self):
		"""
		Publishes an action on the agent's channel.
		"""	
	
	@abc.abstractmethod
	def subscribe(self,*args,**kwargs):
		"""
		Callback invoked by the agent when it is done with an action.
		"""