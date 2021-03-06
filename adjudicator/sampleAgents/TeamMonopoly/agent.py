import copy
import random
from collections import OrderedDict, Counter
from constants import *

import json
import sys
import six
from os import environ
from baseAgent import BaseAgent
from autobahn.twisted.wamp import ApplicationRunner

class Property:
    def __init__(self, id, ownerId, houses, mortgaged):
        self.id = id
        self.ownerId = ownerId
        self.houses = houses
        self.mortgaged = mortgaged


class State(object):
    def __init__(self, stateTuple):
        state = json.loads(stateTuple)
        self.my_id = state['current_player_id']
        self.opponent_id = ""
        for playerId in state['player_ids']:
            if playerId != self.my_id:
                self.opponent_id = playerId
                break
        self.turn = state['turn_number']
        self.player_properties = []
        for id, value in enumerate(state['properties']):
            ownerId = value['ownerId']
            mortgaged = value['mortgaged']
            houses = value['houses']
            self.player_properties.append(Property(id, ownerId, houses, mortgaged))
        self.my_position = state['player_board_positions'][self.my_id]
        self.opponent_position = state['player_board_positions'][self.opponent_id]
        self.my_cash = state['player_cash'][self.my_id]
        self.opponent_cash = state['player_cash'][self.opponent_id]
        self.phase = state['phase']
        self.payload = state['phase_payload']


class Agent(BaseAgent):
    # TODO :: time out decorator & exception handler
    def startGame(self, state):
        self.my_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.utilities = {}
        self.rail_roads = {}  # id:price
        self.monopoly_set = set()
        self.build_buffer_cap = 500
        self.unmortgage_cap = 300
        self.buying_limit = 300
        self.auction_limit = 200
        self.profitable_deal_threshold = 100
        self.mortagaged_cgs = []  # tuple of color, id, unmortgage price
        self.opp_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.opp_utilities = {}
        self.opp_rail_roads = {}  # id:price
        self.opp_mortgaged_props = {}
        self.preference_order = {"Orange": 0,
                                 "Red": 1,
                                 "Yellow": 2,
                                 "Light Blue": 3,
                                 "Brown": 4,
                                 "Green": 5,
                                 "Dark Blue": 6,
                                 "Pink": 7,
                                 "Railroad": 8
                                 }

    @staticmethod
    def get_turns_left(stateobj):
        return 99 - stateobj.turn

    def get_other_agent(self,state):
        return state.opponent_id

    def get_state_object(self, state):
        return State(state)

    def mortgage(self,state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        if stateobj.my_cash > 0:
            return None
        
        lst_properties = self.mortagage_properties(stateobj)
        if lst_properties:
            return lst_properties
        return None

    def unmortgage(self, state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        if stateobj.my_cash < 0:
            return None

        # First preference to unmortgage imp props
        flag = False
        if self.mortagaged_cgs:
            flag = True
            lst_properties = self.unmortgage_property(stateobj)
            if lst_properties:
                return lst_properties
        return None
    
    def sellHouses(self,state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        if stateobj.my_cash > 0:
            return None

        lst_houses = self.sell_house(stateobj)
        if lst_houses:
            return lst_houses
        return None
    
    def buyHouses(self,state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        if stateobj.my_cash < 0:
            return None

        if self.monopoly_set:
            lst_houses = self.build_house(stateobj)
            if lst_houses:
                return lst_houses

        return None

    def getTradeDecision(self,state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)
        return self.get_trade_option(stateobj)

    def endGame(self,state):
        stateobj = self.get_state_object(state)
        if isinstance(stateobj.payload, dict):
            print("Total Stats:")
            print(stateobj.payload)
        else:
            print("************* The winners are {} *************".format(stateobj.payload))

    def update_my_properties(self, stateobj):
        ids = []
        self.my_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.utilities = {}
        self.rail_roads = {}  # id:price
        self.monopoly_set = set()

        my_id = stateobj.my_id
        opponent_id = stateobj.opponent_id

        for propId, prop in enumerate(stateobj.player_properties):
            if propId < 40 and prop.ownerId == my_id and not prop.mortgaged:
                ids.append(propId)
                square_obj = board[propId]
                price = square_obj["price"]
                if square_obj["class"] == "Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = prop.houses
                    self.my_streets[colour][propId] = [build_cost, num_houses, price]
                    if len(self.my_streets[colour]) == square_obj["monopoly_size"]:
                        self.monopoly_set.add(colour)
                elif square_obj["class"] == "Utility":
                    self.utilities[propId] = price
                elif square_obj["class"] == "Railroad":
                    self.rail_roads[propId] = price

    def build_house(self, stateobj):
        self.update_my_properties(stateobj)
        cash_left = stateobj.my_cash - self.build_buffer_cap
        result_dict = Counter()
        # self.update_my_streets(stateobj)
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                continue
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][1]):
                    build_cost, num_houses, p = value[id]
                    if num_houses < 3:
                        if build_cost <= cash_left:
                            result_dict[id] += 1
                            cash_left -= build_cost
                            self.my_streets[color][id][1] += 1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k, v) for k, v in result_dict.items()]

    def mortagage_properties(self, stateobj):
        self.update_my_properties(stateobj)
        # note : only 50%
        debt_left = 0
        if stateobj.my_cash < 0:
            debt_left = -1 * (stateobj.my_cash)

        mortagage_properties_result = []

        # 1) Check 1-10 cells properties
        # 1st mortgage railroad
        if self.rail_roads:
            rail_road_key = list(self.rail_roads.keys())[0]
            if len(self.rail_roads) == 1 and 0 < rail_road_key < 10:
                debt_left -= 0.5 * self.rail_roads[rail_road_key]
                del self.rail_roads[rail_road_key]
                mortagage_properties_result.append(rail_road_key)
            if debt_left <= 0:
                return mortagage_properties_result

        # check for street which is not CG
        marker = []
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                for id, tup in value.items():
                    if tup[1] != 0:
                        continue
                    if 0 < int(id) < 10:
                        debt_left -= 0.5 * tup[2]
                        mortagage_properties_result.append(id)
                        marker.append((color, id))
                        if debt_left <= 0:
                            break
        # delete keys
        for color, id in marker:
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result

        # single utility
        if len(self.utilities) == 1:
            key = list(self.utilities.keys())[0]
            mortagage_properties_result.append(key)
            debt_left -= 0.5 * self.utilities[key]
            self.utilities = {}
        if debt_left <= 0:
            return mortagage_properties_result

        # single railroad
        if len(self.rail_roads) == 1:
            key = list(self.rail_roads.keys())[0]
            mortagage_properties_result.append(key)
            debt_left -= 0.5 * self.rail_roads[key]
            self.rail_roads = {}
        if debt_left <= 0:
            return mortagage_properties_result

        # both utilities
        if len(self.utilities) == 2:
            marker = []
            for id, value in self.utilities.items():
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * value
                marker.append(id)
                if debt_left < 0:
                    break
            for id in marker:
                del self.utilities[id]
        if debt_left <= 0:
            return mortagage_properties_result

        # single street property
        marker = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            if len(dct) == 1:
                id = list(dct.keys())[0]
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(dct[id][2])
                marker.append((color, id))
                if debt_left < 0:
                    break
        for color, id in marker:
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result

        # sell rail road
        marker = []
        for id, price in self.rail_roads.items():
            self.mortagaged_cgs.append(("Railroad", id, price * 0.55))
            mortagage_properties_result.append(id)
            debt_left -= 0.5 * price
            marker.append(id)
            if debt_left < 0:
                break
        for id in marker:
            del self.rail_roads[id]
        if debt_left <= 0:
            return mortagage_properties_result

        # sell all street properties
        marker = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            for id, tup in dct.items():
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(tup[2])
                marker.append((color, id))
                if debt_left < 0:
                    break
        for color, id in marker:
            if color in self.monopoly_set:
                self.mortagaged_cgs.append((color, id, self.my_streets[color][id][2] * 0.55))
                self.monopoly_set.remove(color)
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result

        return mortagage_properties_result

    def get_useless_props(self, stateobj):
        self.update_my_properties(stateobj)
        props_to_trade = []
        # 1) Check 1-10 cells properties
        # check for street which is not CG
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                for id, tup in value.items():
                    if tup[1] != 0:
                        continue
                    if 0 < int(id) < 10:
                        props_to_trade.append(id)

        # single utility
        if len(self.utilities) == 1:
            key = list(self.utilities.keys())[0]
            props_to_trade.append(key)

        # Mortgaged property
        my_id = stateobj.my_id
        mgt_cg_ids = set([t[1] for t in self.mortagaged_cgs])
        for id, prop in enumerate(stateobj.player_properties):
            if prop.ownerId == my_id and prop.mortgaged:
                if id in mgt_cg_ids:
                    continue
                props_to_trade.append(id)

        # single street property
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            if len(dct) == 1 and color not in ['Orange', 'Red', 'Yellow']:
                id = list(dct.keys())[0]
                if dct[id][1] != 0:
                    continue
                props_to_trade.append(id)

        res = []
        for id in props_to_trade:
            space = board[id]
            # Check if his street monopoly is getting formed
            color = space['monopoly']
            if color != "Railroad" and color != "Utility":
                if space['monopoly_size'] - len(self.opp_streets[color]) == 1:
                    continue
            # Check if his utility monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_utilities) == 1:
                continue
            # Check if his railroad monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_rail_roads) == 1:
                continue
            res.append(id)

        # Buffer of all props to clear debt
        buffer_props = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            for id,tup in dct.items():
                if id not in res:
                    buffer_props.append(id)

        return res,buffer_props

    def unmortgage_property(self, stateobj):
        self.update_my_properties(stateobj)
        unmortgage_result = []
        tmp_lst = []
        cash_left = stateobj.my_cash - self.unmortgage_cap
        for color, id, price in sorted(self.mortagaged_cgs, key=lambda x: self.preference_order[x[0]]):
            if cash_left > price:
                cash_left -= price
                tmp_lst.append((color,id,price))
            else:
                for color,id,price in unmortgage_result:
                    self.mortagaged_cgs.remove((color,id,price))
                    unmortgage_result.append(id)
                return unmortgage_result

        # unmortgage all other properties if u have turns
        num_turn_left = self.get_turns_left(stateobj)
        pref = {}
        my_id = stateobj.my_id
        for id, prop in enumerate(stateobj.player_properties):
            if id < 40 and prop.ownerId == my_id and prop.mortgaged:
                square_obj = board[id]
                if square_obj['monopoly'] in pref:
                    pref[square_obj['monopoly']].append(id)
                else:
                    pref[square_obj['monopoly']] = [id]

        # Use the preference order to unmortgage
        for color in self.preference_order:
            if not color in pref:
                continue
            for id in pref[color]:
                if cash_left and num_turn_left > 20:
                    square_obj = board[id]
                    price = square_obj["price"] * 0.55
                    if float(cash_left) > price:
                        cash_left -= price
                        unmortgage_result.append(id)
                    else:
                        return unmortgage_result
                else:
                    return unmortgage_result

    def sell_house(self, stateobj):
        self.update_my_properties(stateobj)
        debt_left = 0
        if stateobj.my_cash < 0:
            debt_left = -1 * (stateobj.my_cash)

        result_dict = Counter()

        marker = []
        for color,value in self.my_streets.items():
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][0], reverse=True):
                    build_cost, num_houses, p = value[id]
                    if num_houses > 0:
                        if debt_left > 0:
                            result_dict[id] += 1
                            debt_left -= (build_cost * 0.5)
                            self.my_streets[key][id][1] -= 1
                            marker.append((key, id))
                        else:
                            flag = 1
                            break
                if flag:
                    break
        if debt_left > 0:
            # let it try mortgaging if selling houses does not clear debt
            for colour, id in marker:
                # fixing changes made to my_streets
                self.my_streets[colour][id][1] += 1
            return []
        return [(k, v) for k, v in result_dict.items()]

    @staticmethod
    def value_of_properties(stateobj, properties_lst):
        total_value = 0
        for id in properties_lst:
            prop = stateobj.player_properties[id]
            if prop.mortgaged:
                total_value += board[id]["price"] * 0.5
            else:
                total_value += board[id]["price"] + (prop.houses * board[id]["build_cost"])
        return total_value

    def net_trade_deal_amount(self, stateobj, cash_offered, cash_requested, properties_offered, properties_requested):
        return cash_offered + self.value_of_properties(stateobj, properties_offered) - cash_requested - \
               self.value_of_properties(stateobj, properties_requested)

    def check_if_any_property_cg(self, properties_requested):
        for prop_id in properties_requested:
            color = board[prop_id]["monopoly"]
            if color in self.monopoly_set:
                return True
        return False

    def can_opponent_form_cg(self, properties_lst):
        for id in properties_lst:
            space = board[id]
            # Check if his street monopoly is getting formed
            monopoly = space['monopoly']
            if monopoly == "Street":
                if space['monopoly_size'] - len(self.opp_streets[monopoly]) == 1 :
                    return True
            # Check if his utility monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_utilities) == 1:
                return True
            # Check if his railroad monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_rail_roads) == 1:
                return True

    def asking_for_another_railroad(self, properties_lst):
        if len(self.opp_rail_roads):
            # find second rail road
            for id in properties_lst:
                space = board[id]
                if space["monopoly"] == "Railroad":
                    return True
        return False

    def respondTrade(self, state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)
        self.update_opp_props(stateobj)
        agentId, cash_offer, properties_offered, cash_requested, properties_requested = stateobj.payload
        # Do not accept if opponent is in debt (ignoring my debt here)
        if stateobj.opponent_cash < 0:
            return False

        net_amount = self.net_trade_deal_amount(stateobj, cash_offer,
                                                cash_requested, properties_offered,
                                                properties_requested)

        # You are not in debt
        if net_amount > self.profitable_deal_threshold:
            # if he is asking our cg reject
            if self.check_if_any_property_cg(properties_requested):
                return False
            # if his cg complete then also reject
            if self.can_opponent_form_cg(properties_requested):
                return False
            # if asking for another rail road reject
            if self.asking_for_another_railroad(properties_requested):
                return False
            else:
                return True
        else:
            return False

    def update_opp_props(self, stateobj):
        opp_id = self.get_other_agent(stateobj)
        self.opp_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.opp_utilities = {}
        self.opp_rail_roads = {}  # id:price
        self.opp_mortgaged_props = {}
        opponent_id = stateobj.opponent_id
        for id, prop in enumerate(stateobj.player_properties):
            if id < 40 and prop.ownerId == opponent_id:
                square_obj = board[id]
                price = square_obj["price"]
                if prop.mortgaged:
                    self.opp_mortgaged_props[id] = price
                    continue
                if square_obj["class"] == "Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    self.opp_streets[colour][id] = (build_cost, prop.houses, price)
                    # if len(self.opp_streets[colour][id]) == square_obj["monopoly_size"]:
                    #     self.monopoly_set.add(colour)
                elif square_obj["class"] == "Utility":
                    self.opp_utilities[id] = price
                elif square_obj["class"] == "Railroad":
                    self.opp_rail_roads[id] = price

    def get_trade_option(self, stateobj):
        # Get opponent properties - utilities, railroads, mortgaged properties, cgs, other props
        self.update_opp_props(stateobj)
        self.update_my_properties(stateobj)

        # TODO: check opponent cash before returning

        # Try to get properties to request by looking at CG in
        # preference order (O,R,Y only) + utility + railroad
        props_req = []
        for color, values in self.my_streets.items():
            if color in self.monopoly_set or color in ['Brown', 'Green', 'Dark Blue', 'Pink']:
                continue
            if not values:
                continue
            any_id = list(values.keys())[0]
            grp_elements = board[any_id]['monopoly_group_elements']
            if len(grp_elements) == len(values):
                grp_elements.append(any_id)
                props_req.append(list(set(grp_elements) - set(values))[0])

        if len(self.utilities) == 1 and len(self.opp_utilities) == 1:
            props_req.append(list(self.opp_utilities.keys())[0])

        useless_props, buffer = self.get_useless_props(stateobj)
        giveaway_props = copy.deepcopy(useless_props)
        giveaway_props.extend(buffer)

        debt_left = 0
        if stateobj.my_cash < 0:
            debt_left = -1 * (stateobj.my_cash)

        if len(self.rail_roads) > 0 and len(self.opp_rail_roads) > 0:
            # Strategy 3: If we have one railroad, get railroad from him
            # & give prop without forming cg to him
            tmp_lst = []
            id = list(self.opp_rail_roads.keys())[0]
            cash_to_match = board[id]['price'] + debt_left
            for useless_prop in useless_props:
                cash_to_match -= board[useless_prop]['price']
                tmp_lst.append(useless_prop)
                if cash_to_match > 0:
                    continue
                else:
                    cash_req = abs(cash_to_match)
                    return [stateobj.opponent_id, 0, tmp_lst, cash_req, [id]]
        else:
            if random.randint(1, 101) % 2:
                # Strategy 1 (taking care of debt + requesting imp props)
                if props_req and useless_props:
                    for prop in props_req:
                        tmp_lst = []
                        cash_to_match = board[prop]['price'] + debt_left
                        for id in useless_props:
                            # trying all combinations of useless prop and prop to offer
                            cash_to_match -= board[id]['price']
                            tmp_lst.append(id)
                            if cash_to_match > 0:
                                continue
                            else:
                                cash_req = abs(cash_to_match)
                                return [stateobj.opponent_id, 0, tmp_lst, cash_req, [prop]]
                        if cash_to_match > 0:
                            continue
                elif not useless_props:
                    for prop in props_req:
                        cash_offer = board[prop]['price']
                        if stateobj.my_cash >= cash_offer + 300:
                            return [stateobj.opponent_id, cash_offer, [], 0, [prop]]
            else:
                # Strategy 2: taking care of debt + giving off useless
                # props by asking for cash
                if useless_props:
                    tmp_lst = []
                    # TODO: For nw, trying to snatch 300 from the opponent
                    cash_to_match = debt_left + 300
                    for id in useless_props:
                        # trying all combinations of useless prop and prop to offer
                        cash_to_match -= board[id]['price']
                        tmp_lst.append(id)
                        if cash_to_match > 0:
                            continue
                        else:
                            cash_req = abs(cash_to_match)
                            return [stateobj.opponent_id, 0, tmp_lst, cash_req, []]

        # TODO: Trade reverse order preference of street class
        # Backup Strategy (taking care of debt by giving away useless props)
        if debt_left and giveaway_props:
            tmp_lst = []
            cash_to_match = debt_left
            for id in giveaway_props:
                # trying all combinations of useless prop and prop to offer
                cash_to_match -= board[id]['price']
                tmp_lst.append(id)
                if cash_to_match > 0:
                    continue
                else:
                    cash_req = abs(cash_to_match)
                    return [stateobj.opponent_id, 0, tmp_lst, cash_req, []]

        return None

    def buyProperty(self, state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        # Check if we reached buying cap
        if stateobj.my_cash <= self.buying_limit:
            return False

        # check if less number of turns left
        if self.get_turns_left(stateobj) < 20:
            return False

        # get class of property landed on
        propertyId = stateobj.my_position
        space = board[propertyId]
        if space['class'] == 'Railroad':
            # blind yes!
            return True
        elif space['class'] == 'Street':
            # Check if it is forming monopoly
            monopoly_size = space['monopoly_size']
            num_props_cg = len(self.my_streets[space['monopoly']])
            if num_props_cg + 1 == monopoly_size:
                # definitely buy
                return True

            # Check if it is important to opponent
            opp_id = stateobj.opponent_id
            is_imp = True
            for propid in space['monopoly_group_elements']:
                prop = stateobj.player_properties[propid]
                if prop.ownerId != opp_id:
                    is_imp = False
            if is_imp:
                return True

            # Check if it is important to us
            # TODO: try this logic
            if space['monopoly'] in ['Orange', 'Red', 'Yellow', 'Light Blue']:
                return True
            else:
                # Look for auction if we are not interested in property
                return False

        elif space['class'] == 'Utility':
            # TBD
            return False

    def auctionProperty(self, state):
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)

        # if cash less than limit don't bid
        if stateobj.my_cash <= self.auction_limit:
            return 0

        # get property ID
        propid = stateobj.payload
        space = board[propid]

        # check if less number of turns left
        if self.get_turns_left(stateobj) < 20:
            # Check if we reached auction cap
            if stateobj.my_cash <= self.auction_limit:
                return 0
            else:
                return 0.5 * space['price']

        # Check if property is imp to u
        # Then bid for prop val + 1
        # Check if it is forming monopoly
        bid = 0
        if space['class'] == 'Street':
            monopoly_size = space['monopoly_size']
            num_props_cg = len(self.my_streets[space['monopoly']])
            if num_props_cg + 1 == monopoly_size:
                bid = space['price'] + 1
        # Check if it is second rail road or more
        if space['class'] == 'Railroad' and \
                len(self.rail_roads) > 1:
            bid = space['price'] + 1
        # Check if it is second utility
        if space['class'] == 'Utility' and \
                len(self.utilities) > 1:
            bid = 0.8 * space['price'] + 1

        # Check if bid is greater than available cash
        if stateobj.my_cash <= bid:
            return 100
        elif bid:
            return bid

        # Check if property imp for him
        opp_id = stateobj.opponent_id
        is_imp = True
        for _propid in space['monopoly_group_elements']:
            prop = stateobj.player_properties[_propid]
            if prop.ownerId != opp_id:
                is_imp = False
        if is_imp:
            # if his cash is less, his cash + 1
            if stateobj.opponent_cash < space['price']:
                bid = stateobj.opponent_cash + 1
            else:
                # else he has cash but wants to buy for less, 0.9 * prop val
                bid = 0.9 * space['price']

        # Check if bid is greater than available cash
        if stateobj.my_cash <= bid:
            return 100
        elif bid:
            return bid

        # TODO: keep checking prev pattern from receive state
        # then get all formulas & apply

        # generically, bid for 0.5 * prop val + 1
        default = 0.5 * space['price'] + 1
        return default if default + 100 < stateobj.my_cash else 100

    def jailDecision(self, state):
        stateobj = self.get_state_object(state)
        if self.get_turns_left(stateobj) < 30 or stateobj.my_cash < 50:
            return 'R'

        if stateobj.my_id == stateobj.player_properties[40].ownerId:
            return ['C', 40]
        elif stateobj.my_id == stateobj.player_properties[41].ownerId:
            return ['C', 41]
        else:
            return 'P'

if __name__ == '__main__':
    #url = environ.get("CBURL", u"ws://localhost:4000/ws")
    url = environ.get("CBURL", u"ws://monopoly-ai.com/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(Agent)