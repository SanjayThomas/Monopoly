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
  return 'ownerId' in property && property.ownerId === myId;
};

export const getColors = () => {
  return ['red','blue','green','gold','cyan','magenta','orange','pink']
};

const completedMonopoly = (properties, property, myId) => {
  const group_elements = property.monopoly_group_elements;
  for (let index = 0; index < group_elements.length; index++) {
    const group_element = group_elements[index];
    if (!amIOwner(properties[group_element], myId)) return false;
  }
  return true;
};

const buySellFilter = (property, properties, myId) => {
  if (property.class !== "street") return false;
  if (!amIOwner(property, myId)) return false;
  if (!completedMonopoly(properties, property, myId)) return false;
  return true;
};

export const getBuyingCandidates = (properties, myId) => {
  const candidates = properties
    .filter(property => buySellFilter(property, properties, myId) && (property.houses < 5))
    .map(property => property.id);
  return candidates;
};

export const getSellingCandidates = (properties, myId) => {
  const candidates = properties
    .filter(property => buySellFilter(property, properties, myId) && (property.houses > 0))
    .map(property => property.id);
  return candidates;
};

export const getTradeCandidates = (properties, playerId) => {
  return properties.filter(property => mortgageFilter(property, properties, playerId))
    .map(property => property.id);
};

const mortgageFilter = (property, properties, myId) => {
  if (property.class !== "street" && property.class !== "utility" && property.class !== "railroad") return false;
  if (!amIOwner(property, myId)) return false;
  if (property.houses > 0) return false;

  const group_elements = property.monopoly_group_elements;
  for (let index = 0; index < group_elements.length; index++) {
    const group_element = group_elements[index];
    if (properties[group_element].houses > 0) return false;
  }
  return true;
};

export const getMortgageCandidates = (properties, myId) => {
  return properties
    .filter(property => {
      if (property.mortgaged) return false;
      return mortgageFilter(property, properties, myId);
    })
    .map(property => property.id);
};

export const getUnmortgageCandidates = (properties, myId) => {
  return properties
    .filter(property => {
      if (!property.mortgaged) return false;
      return mortgageFilter(property, properties, myId);
    })
    .map(property => property.id);
};

export const convertTimer = timer => {
    let min = Math.floor(timer/60);
    let sec = timer%60;

    if (sec < 10) {
      sec = "0" + sec;
    }
    if (min < 10) {
      min = "0" + min;
    }

    return min+":"+sec;
  };
