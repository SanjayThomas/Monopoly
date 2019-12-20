const properties = [
  {
    id: 0,
    class: "corner go",
    name: "Go",
    monopoly: "None",
    instructions: "Collect $200.00 salary as you pass"
  },
  {
    id: 1,
    class: "street",
    name: "Mediterranean Avenue",
    monopoly: "brown",
    monopoly_size: 2,
    price: 60,
    build_cost: 50,
    rent: [2, 10, 30, 90, 160, 250],
    tax: 0,
    monopoly_group_elements: [3],
    monopoly_group_id: 0
  },
  {
    id: 2,
    class: "chest",
    name: "Community Chest",
    instructions: "Follow instructions on top card"
  },
  {
    id: 3,
    class: "street",
    name: "Baltic Avenue",
    monopoly: "brown",
    monopoly_size: 2,
    price: 60,
    build_cost: 50,
    rent: [4, 20, 60, 180, 320, 450],
    tax: 0,
    monopoly_group_elements: [1],
    monopoly_group_id: 0
  },
  {
    id: 4,
    class: "income-tax",
    name: "Income Tax",
    tax: 200
  },
  {
    id: 5,
    class: "railroad",
    name: "Reading Railroad",
    monopoly: "Railroad",
    monopoly_size: 4,
    price: 200,
    build_cost: 0,
    rent: [25, 50, 100, 200, 0, 0],
    tax: 0,
    monopoly_group_elements: [15, 25, 35],
    monopoly_group_id: 1
  },
  {
    id: 6,
    class: "street",
    name: "Oriental Avenue",
    monopoly: "light-blue",
    monopoly_size: 3,
    price: 100,
    build_cost: 50,
    rent: [6, 30, 90, 270, 400, 550],
    tax: 0,
    monopoly_group_elements: [8, 9],
    monopoly_group_id: 2
  },
  {
    id: 7,
    class: "chance",
    name: "Chance",
    instructions: "Follow instructions on top card"
  },
  {
    id: 8,
    class: "street",
    name: "Vermont Avenue",
    monopoly: "light-blue",
    monopoly_size: 3,
    price: 100,
    build_cost: 50,
    rent: [6, 30, 90, 270, 400, 550],
    tax: 0,
    monopoly_group_elements: [6, 9],
    monopoly_group_id: 2
  },
  {
    id: 9,
    class: "street",
    name: "Connecticut Avenue",
    monopoly: "light-blue",
    monopoly_size: 3,
    price: 120,
    build_cost: 50,
    rent: [8, 40, 100, 300, 450, 600],
    tax: 0,
    monopoly_group_elements: [6, 8],
    monopoly_group_id: 2
  },
  {
    id: 10,
    class: "corner jail",
    name: "Jail"
  },
  {
    id: 11,
    class: "street",
    name: "St. Charles Place",
    monopoly: "pink",
    monopoly_size: 3,
    price: 140,
    build_cost: 100,
    rent: [10, 50, 150, 450, 625, 750],
    tax: 0,
    monopoly_group_elements: [13, 14],
    monopoly_group_id: 3
  },
  {
    id: 12,
    class: "utility",
    name: "Electric Company",
    monopoly: "Utility",
    monopoly_size: 2,
    price: 150,
    build_cost: 0,
    rent: [4, 10, 0, 0, 0, 0],
    tax: 0,
    monopoly_group_elements: [28],
    monopoly_group_id: 4
  },
  {
    id: 13,
    class: "street",
    name: "States Avenue",
    monopoly: "pink",
    monopoly_size: 3,
    price: 140,
    build_cost: 100,
    rent: [10, 50, 150, 450, 625, 750],
    tax: 0,
    monopoly_group_elements: [11, 14],
    monopoly_group_id: 3
  },
  {
    id: 14,
    class: "street",
    name: "Virginia Avenue",
    monopoly: "pink",
    monopoly_size: 3,
    price: 160,
    build_cost: 100,
    rent: [12, 60, 180, 500, 700, 900],
    tax: 0,
    monopoly_group_elements: [11, 13],
    monopoly_group_id: 3
  },
  {
    id: 15,
    class: "railroad",
    name: "Pennsylvania Railroad",
    monopoly: "railroad",
    monopoly_size: 4,
    price: 200,
    build_cost: 0,
    rent: [25, 50, 100, 200, 0, 0],
    tax: 0,
    monopoly_group_elements: [5, 25, 35],
    monopoly_group_id: 1
  },
  {
    id: 16,
    class: "street",
    name: "St. James Place",
    monopoly: "orange",
    monopoly_size: 3,
    price: 180,
    build_cost: 100,
    rent: [14, 70, 200, 550, 750, 950],
    tax: 0,
    monopoly_group_elements: [18, 19],
    monopoly_group_id: 5
  },
  {
    id: 17,
    class: "chest",
    name: "Community Chest",
    instructions: "Follow instructions on top card"
  },
  {
    id: 18,
    class: "street",
    name: "Tennessee Avenue",
    monopoly: "orange",
    monopoly_size: 3,
    price: 180,
    build_cost: 100,
    rent: [14, 70, 200, 550, 750, 950],
    tax: 0,
    monopoly_group_elements: [16, 19],
    monopoly_group_id: 5
  },
  {
    id: 19,
    class: "street",
    name: "New York Avenue",
    monopoly: "orange",
    monopoly_size: 3,
    price: 200,
    build_cost: 100,
    rent: [16, 80, 220, 600, 800, 1000],
    tax: 0,
    monopoly_group_elements: [16, 18],
    monopoly_group_id: 5
  },
  {
    id: 20,
    class: "corner free-parking",
    name: "Free Parking"
  },
  {
    id: 21,
    class: "street",
    name: "Kentucky Avenue",
    monopoly: "red",
    monopoly_size: 3,
    price: 220,
    build_cost: 150,
    rent: [18, 90, 250, 700, 875, 1050],
    tax: 0,
    monopoly_group_elements: [23, 24],
    monopoly_group_id: 6
  },
  {
    id: 22,
    class: "chance",
    name: "Chance",
    instructions: "Follow instructions on top card"
  },
  {
    id: 23,
    class: "street",
    name: "Indiana Avenue",
    monopoly: "red",
    monopoly_size: 3,
    price: 220,
    build_cost: 150,
    rent: [18, 90, 250, 700, 875, 1050],
    tax: 0,
    monopoly_group_elements: [21, 24],
    monopoly_group_id: 6
  },
  {
    id: 24,
    class: "street",
    name: "Illinois Avenue",
    monopoly: "red",
    monopoly_size: 3,
    price: 240,
    build_cost: 150,
    rent: [20, 100, 300, 750, 925, 1100],
    tax: 0,
    monopoly_group_elements: [21, 23],
    monopoly_group_id: 6
  },
  {
    id: 25,
    class: "Railroad",
    name: "B. & O. Railroad",
    monopoly: "Railroad",
    monopoly_size: 4,
    price: 200,
    build_cost: 0,
    rent: [25, 50, 100, 200, 0, 0],
    tax: 0,
    monopoly_group_elements: [5, 15, 35],
    monopoly_group_id: 1
  },
  {
    id: 26,
    class: "street",
    name: "Atlantic Avenue",
    monopoly: "yellow",
    monopoly_size: 3,
    price: 260,
    build_cost: 150,
    rent: [22, 110, 330, 800, 975, 1150],
    tax: 0,
    monopoly_group_elements: [27, 29],
    monopoly_group_id: 7
  },
  {
    id: 27,
    class: "street",
    name: "Ventnor Avenue",
    monopoly: "yellow",
    monopoly_size: 3,
    price: 260,
    build_cost: 150,
    rent: [22, 110, 330, 800, 975, 1150],
    tax: 0,
    monopoly_group_elements: [26, 29],
    monopoly_group_id: 7
  },
  {
    id: 28,
    class: "utility",
    name: "Water Works",
    monopoly: "Utility",
    monopoly_size: 2,
    price: 150,
    build_cost: 0,
    rent: [4, 10, 0, 0, 0, 0],
    tax: 0,
    monopoly_group_elements: [12],
    monopoly_group_id: 4
  },
  {
    id: 29,
    class: "street",
    name: "Marvin Gardens",
    monopoly: "yellow",
    monopoly_size: 3,
    price: 280,
    build_cost: 150,
    rent: [24, 120, 360, 850, 1025, 1200],
    tax: 0,
    monopoly_group_elements: [26, 27],
    monopoly_group_id: 7
  },
  {
    id: 30,
    class: "go-to-jail",
    name: "Go To Jail"
  },

  {
    id: 31,
    class: "street",
    name: "Pacific Avenue",
    monopoly: "green",
    monopoly_size: 3,
    price: 300,
    build_cost: 200,
    rent: [26, 130, 390, 900, 1100, 1275],
    tax: 0,
    monopoly_group_elements: [32, 34],
    monopoly_group_id: 8
  },
  {
    id: 32,
    class: "street",
    name: "North Carolina Avenue",
    monopoly: "green",
    monopoly_size: 3,
    price: 300,
    build_cost: 200,
    rent: [26, 130, 390, 900, 1100, 1275],
    tax: 0,
    monopoly_group_elements: [31, 34],
    monopoly_group_id: 8
  },
  {
    id: 33,
    class: "chest",
    name: "Community Chest"
  },
  {
    id: 34,
    class: "street",
    name: "Pennsylvania Avenue",
    monopoly: "green",
    monopoly_size: 3,
    price: 320,
    build_cost: 200,
    rent: [28, 150, 450, 1000, 1200, 1400],
    tax: 0,
    monopoly_group_elements: [31, 32],
    monopoly_group_id: 8
  },
  {
    id: 35,
    class: "railroad",
    name: "Short Line",
    monopoly: "Railroad",
    monopoly_size: 4,
    price: 200,
    build_cost: 0,
    rent: [25, 50, 100, 200, 0, 0],
    tax: 0,
    monopoly_group_elements: [5, 15, 25],
    monopoly_group_id: 1
  },
  {
    id: 36,
    class: "chance",
    name: "Chance",
  },
  {
    id: 37,
    class: "street",
    name: "Park Place",
    monopoly: "dark-blue",
    monopoly_size: 2,
    price: 350,
    build_cost: 200,
    rent: [35, 175, 500, 1100, 1300, 1500],
    tax: 0,
    monopoly_group_elements: [39],
    monopoly_group_id: 9
  },
  {
    id: 38,
    class: "luxury-tax",
    name: "Luxury Tax",
    tax: 100
  },
  {
    id: 39,
    class: "street",
    name: "Boardwalk",
    monopoly: "dark-blue",
    monopoly_size: 2,
    price: 400,
    build_cost: 200,
    rent: [50, 200, 600, 1400, 1700, 2000],
    tax: 0,
    monopoly_group_elements: [37],
    monopoly_group_id: 9
  },
  {
    id: 40,
    class: "jail-free-card",
    name: "Chance Get out of Jail Free Card"
  },
  {
    id: 41,
    class: "jail-free-card",
    name: "Community Get out of Jail Free Card"
  }
];

export default properties;
