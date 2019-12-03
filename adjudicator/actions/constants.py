from state import Phase

PASSING_GO_MONEY = 200
# max no of turns in the game
TOTAL_NO_OF_TURNS = 100
INITIAL_CASH = 1500
MAX_TRADES = 2

BOARD_SIZE = 40
CHANCE_GET_OUT_OF_JAIL_FREE = 40
COMMUNITY_GET_OUT_OF_JAIL_FREE = 41
JUST_VISTING = 10
JAIL = -1

MEDAVE_BUILDCOST = 50

MONOPOLY_GROUPS = [
	[1,3],
	[6,8,9],
	[11,13,14],
	[16,18,19],
	[21,23,24],
	[26,27,29],
	[31,32,34],
	[37,39]
]

# if phase is not listed, default action is None
DEFAULT_ACTIONS = {
	Phase.JAIL           : ("P",),
	Phase.BUY            : False,
	Phase.AUCTION        : 0,
	Phase.TRADE_RESPONSE : False
}