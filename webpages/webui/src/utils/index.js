export const substituteEndpoint = (endpoint, agentId, gameId) => {
  endpoint = endpoint.replace(/{%game_id%}/g, gameId);
  endpoint = endpoint.replace(/{%agent_id%}/g, agentId);
  return endpoint;
};

export const mergeProperties = (current, incoming) => {
  const merged = current.map((property, index) => {
    return {
      ...property,
      ...incoming[index]
    };
  });

  return merged;
};

export const calculateRent = (playerDebts, playerId) => {
  let debts = playerDebts[playerId];
  const otherPlayerDebts = debts.otherPlayers;
  let totalDebts = 0;
  totalDebts += debts.bank;
  for (let otherPlayer in otherPlayerDebts) {
    totalDebts += otherPlayerDebts[otherPlayer];
  }

  return totalDebts;
};

export const getPlayerName = (myId, id) => {
  if (myId === id) {
    return "human";
  }
  return "robot";
};

// https://stackoverflow.com/questions/3895478/does-javascript-have-a-method-like-range-to-generate-a-range-within-the-supp
export const range = (size, startAt = 0) => {
  return [...Array(size).keys()].map(i => i + startAt);
};

export const adjustPlayerPositions = playersPositions => {
  return Object.keys(playersPositions).reduce((adjusted, playerId) => {
    if (playersPositions[playerId] === -1) {
      adjusted[playerId] = 10;
    } else {
      adjusted[playerId] = playersPositions[playerId];
    }
    return adjusted;
  }, {});
};

const amIOwner = (property, myId) => {
  return property.owned === true && property.ownerId === myId;
};

const completedMonopoly = (properties, property, myId) => {
  const group_elements = property.monopoly_group_elements;
  for (let index = 0; index < group_elements.length; index++) {
    const group_element = group_elements[index];
    if (!amIOwner(properties[group_element], myId)) return false;
  }
  return true;
};

const getBSMCandidates = state => {
  const { properties, myId } = state;

  return properties.filter(property => {
    if (property.class !== "street") return false;
    if (!amIOwner(property, myId)) return false;
    if (!completedMonopoly(properties, property, myId)) return false;
    return true;
  });
};

export const getBuyingCandidates = state => {
  const candidates = getBSMCandidates(state)
    .filter(property => property.houses < 5)
    .map(property => property.id);
  return candidates;
};

export const getSellingCandidates = state => {
  return getBSMCandidates(state)
    .filter(property => property.houses > 0)
    .map(property => property.id);
};

const constructionsInMonopolyGroup = (properties, property, myId) => {
  const group_elements = property.monopoly_group_elements;
  for (let index = 0; index < group_elements.length; index++) {
    const group_element = group_elements[index];
    if (properties[group_element].houses > 0 || properties[group_element].hotel)
      return false;
  }
};

export const getMortgageCandidates = state => {
  const { properties, myId } = state;

  return properties
    .filter(property => {
      if (property.mortgaged) return false;
      if (!amIOwner(property, myId)) return false;
      if (property.houses > 0 || property.hotel) return false;
      // if (
      //   completedMonopoly(properties, property, myId) &&
      //   constructionsInMonopolyGroup(properties, property, myId)
      // )
      //   return false;

      return true;
    })
    .map(property => property.id);
};
