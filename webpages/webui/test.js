const state = require("./data");


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

const getBuyingCandidates = state => {
  return getBSMCandidates(state)
    .filter(property => property.houses < 5)
    .map(property => property.id);
};

const getSellingCandidates = state => {
  return getBSMCandidates(state)
    .filter(property => property.houses > 0)
    .map(property => property.id);
};

const getMortgageCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "street") return false;
      if (property.mortgaged) return false;
      if (!amIOwner(property, myId)) return false;
      //even if it is a completed monopoly there shouldn't be any constructions?
      if (property.houses > 0 || property.hotel) return false;
      return true;
    })
    .map(property => property.id);

  return candidates;
};


const myId = "iwWxalZSKSMKvSPZBtxFl7Bbko1OTeBAT7IReUmU0engIoJqmU";
const properties = Object.values(state);
const newState = {properties,myId};
console.log(getBuyingCandidates(newState));