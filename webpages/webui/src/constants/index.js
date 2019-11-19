export const ROUTER_ENDPOINT = "ws://localhost:4000/ws";
export const APPLICATION_REALM = "realm1";

// action button string

export const TRADE_ACTION = "trade";
export const AUCTION_ACTION = "auction";
export const BSM_ACTION = "bsm";
export const JAIL_DECISION_ACTION = "jail";

// endpoints
export const JOIN_GAME_ENDPOINT = "com.game{%game_id%}.joingame";

export const Phase = {
  NO_ACTION: 0,
  TRADE: 1,
  DICE_ROLL: 2,
  BUYING: 3,
  AUCTION: 4,
  PAYMENT: 5,
  JAIL: 6,
  CHANCE_CARD: 7,
  COMMUNITY_CHEST_CARD: 8,
  TRADE_RESPONSE: 9
};

export const PhaseNameMapping = {
  1: "trade",
  2: "dice_roll",
  3: "buying",
  4: "auction",
  5: "payment",
  6: "jail",
  7: "chance_card",
  8: "community_chest_card",
  9: "trade_response"
};

export const communityChestCards = [
  {
    id: 0,
    content: "Advance to Go (Collect $200)",
    type: 3,
    position: 1,
    money: 0,
    money2: 0
  },
  {
    id: 1,
    content: "Bank error in your favor, collect $200",
    type: 1,
    position: 0,
    money: 200,
    money2: 0
  },
  {
    id: 2,
    content: "Doctor's fees, Pay $50",
    type: 1,
    position: 0,
    money: -50,
    money2: 0
  },
  {
    id: 3,
    content: "From sale of stock you get $50",
    type: 1,
    position: 0,
    money: 50,
    money2: 0
  },
  {
    id: 4,
    content: "Get out of jail free, this card may be kept until needed",
    type: 4,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 5,
    content:
      "Go to jail, go directly to jail – Do not pass Go, do not collect $200",
    type: 3,
    position: -1,
    money: 0,
    money2: 0
  },
  {
    id: 6,
    content:
      "Grand Opera Night. Collect $50 from every player for opening night seats.",
    type: 2,
    position: 0,
    money: 50,
    money2: 0
  },
  {
    id: 7,
    content: "Holiday Fund matures - Receive $100",
    type: 1,
    position: 0,
    money: 100,
    money2: 0
  },
  {
    id: 8,
    content: "Income Tax refund. Collect $20",
    type: 1,
    position: 0,
    money: 20,
    money2: 0
  },
  {
    id: 9,
    content: "Life Insurance Matures - Collect $100",
    type: 1,
    position: 0,
    money: 100,
    money2: 0
  },
  {
    id: 10,
    content: "Pay Hospital Fees of $50",
    type: 1,
    position: 0,
    money: -50,
    money2: 0
  },
  {
    id: 11,
    content: "Pay School Fees of $50",
    type: 1,
    position: 0,
    money: -50,
    money2: 0
  },
  {
    id: 12,
    content: "Receive $25 Consultancy Fee",
    type: 1,
    position: 0,
    money: 25,
    money2: 0
  },
  {
    id: 13,
    content:
      "You are assessed for street repairs: Pay $40 per house and $115 per hotel you own.",
    type: 5,
    position: 0,
    money: -40,
    money2: -115
  },
  {
    id: 14,
    content: "You have won second prize in a beauty contest– collect $10",
    type: 1,
    position: 0,
    money: 10,
    money2: 0
  },
  {
    id: 15,
    content: "You inherit $100",
    type: 1,
    position: 0,
    money: 100,
    money2: 0
  }
];

export const chanceCards = [
  {
    id: 0,
    content: "Advance to Go (Collect $200)",
    type: 3,
    position: 1,
    money: 0,
    money2: 0
  },
  {
    id: 1,
    content: "Advance to Illinois Ave. If you pass Go, collect $200.",
    type: 3,
    position: 25,
    money: 0,
    money2: 0
  },
  {
    id: 2,
    content: "Advance to St. Charles Place. If you pass Go, collect $200",
    type: 3,
    position: 12,
    money: 0,
    money2: 0
  },
  {
    id: 3,
    content:
      "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total 10 times the amount thrown.",
    type: 7,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 4,
    content:
      "Advance token to the nearest Railroad and pay owner twice the rental to which he/she {he} is otherwise entitled. If Railroad is unowned, you may buy it from the Bank",
    type: 6,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 5,
    content:
      "Advance token to the nearest Railroad and pay owner twice the rental to which he/she {he} is otherwise entitled. If Railroad is unowned, you may buy it from the Bank",
    type: 6,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 6,
    content: "Bank pays you dividend of $50",
    type: 1,
    position: 0,
    money: 50,
    money2: 0
  },
  {
    id: 7,
    content:
      "Get out of Jail free, this card may be kept until needed, or traded",
    type: 4,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 8,
    content: "Go Back 3 Spaces",
    type: 8,
    position: 0,
    money: 0,
    money2: 0
  },
  {
    id: 9,
    content:
      "Go to Jail. Go directly to Jail. Do not pass GO, do not collect $200.",
    type: 3,
    position: -1,
    money: 0,
    money2: 0
  },
  {
    id: 10,
    content:
      "Make general repairs on all your property: For each house pay $25, For each hotel {pay} $100.",
    type: 5,
    position: 0,
    money: -25,
    money2: -100
  },
  {
    id: 11,
    content: "Pay poor tax of $15",
    type: 1,
    position: 0,
    money: -15,
    money2: 0
  },
  {
    id: 12,
    content: "Take a trip to Reading Railroad.",
    type: 3,
    position: 6,
    money: 0,
    money2: 0
  },
  {
    id: 13,
    content: "Advance to Boardwalk",
    type: 3,
    position: 40,
    money: 0,
    money2: 0
  },
  {
    id: 14,
    content: "You have been elected chairman of the board, pay each player $50",
    type: 2,
    position: 0,
    money: -50,
    money2: 0
  },
  {
    id: 15,
    content: "Your building loan matures, collect $150",
    type: 1,
    position: 0,
    money: 150,
    money2: 0
  }
];
