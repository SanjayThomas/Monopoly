from collections import namedtuple

Position = namedtuple("Position", "type name group groupSize price houseCost rents tax groupMembers probability")
Rents = namedtuple("Rents", "default house1 house2 house3 house4 hotel")

MAX_HOUSES = 32
MAX_HOTELS = 12
CHANCE_GOJF_PROPERTY = 40
COMMUNITY_GOJF_PROPERTY = 41
CHANCE_GOJF_CARD = 7
COMMUNITY_GOJF_CARD = 4

class Type:
    PROPERTY = 0
    RAILROAD = 1
    UTILITY = 2
    CHANCE = 3
    COMMUNITY = 4
    SPECIAL = 5

class Group:
    BROWN = 0
    LIGHT_BLUE = 1
    PINK = 2
    ORANGE = 3
    RED = 4
    YELLOW = 5
    GREEN = 6
    DARK_BLUE = 7
    RAILROAD = 8
    UTILITY = 9
    NONE = 10

board = [
    Position(Type.SPECIAL, "GO", Group.NONE, 0, 0, 0, None, 0, (), 0.030961),
    Position(Type.PROPERTY, "Mediterranean Avenue", Group.BROWN, 2, 60, 50, Rents(2, 10, 30, 90, 160, 250), 0, (1, 3), 0.021314),
    Position(Type.COMMUNITY, "Community Chest", Group.NONE, 0, 0, 0, None, 0, (), 0.018849),
    Position(Type.PROPERTY, "Baltic Avenue", Group.BROWN, 2, 60, 50, Rents(4, 20, 60, 180, 320, 450), 0, (1, 3), 0.021624),
    Position(Type.SPECIAL, "Income Tax", Group.NONE, 0, 0, 0, None, 200, (), 0.023285),
    Position(Type.RAILROAD, "Reading Railroad", Group.RAILROAD, 4, 200, 0, None, 0, (5, 15, 25, 35), 0.029631),
    Position(Type.PROPERTY, "Oriental Avenue", Group.LIGHT_BLUE, 3, 100, 50, Rents(6, 30, 90, 270, 400, 550), 0, (6, 8, 9), 0.022621),
    Position(Type.CHANCE, "Chance", Group.NONE, 0, 0, 0, None, 0, (), 0.008650),
    Position(Type.PROPERTY, "Vermont Avenue", Group.LIGHT_BLUE, 3, 100, 50, Rents(6, 30, 90, 270, 400, 550), 0, (6, 8, 9), 0.023210),
    Position(Type.PROPERTY, "Connecticut Avenue", Group.LIGHT_BLUE, 3, 120, 50, Rents(8, 40, 100, 300, 450, 600), 0, (6, 8, 9), 0.023003),
    Position(Type.SPECIAL, "Just Visiting", Group.NONE, 0, 0, 0, None, 0, (), 0.022695),
    Position(Type.PROPERTY, "St. Charles Place", Group.PINK, 3, 140, 100, Rents(10, 50, 150, 450, 625, 750), 0, (11, 13, 14), 0.027017),
    Position(Type.UTILITY, "Electric Company", Group.UTILITY, 2, 150, 0, None, 0, (12, 28), 0.026040),
    Position(Type.PROPERTY, "States Avenue", Group.PINK, 3, 140, 100, Rents(10, 50, 150, 450, 625, 750), 0, (11, 13, 14), 0.023721),
    Position(Type.PROPERTY, "Virginia Avenue", Group.PINK, 3, 160, 100, Rents(12, 60, 180, 500, 700, 900), 0, (11, 13, 14), 0.024649),
    Position(Type.RAILROAD, "Pennsylvania Railroad", Group.RAILROAD, 4, 200, 0, None, 0, (5, 15, 25, 35), 0.029200),
    Position(Type.PROPERTY, "St. James Place", Group.ORANGE, 3, 180, 100, Rents(14, 70, 200, 550, 750, 950), 0, (16, 18, 19), 0.027924),
    Position(Type.COMMUNITY, "Community Chest", Group.NONE, 0, 0, 0, None, 0, (), 0.025945),
    Position(Type.PROPERTY, "Tennessee Avenue", Group.ORANGE, 3, 180, 100, Rents(14, 70, 200, 550, 750, 950), 0, (16, 18, 19), 0.029356),
    Position(Type.PROPERTY, "New York Avenue", Group.ORANGE, 3, 200, 100, Rents(16, 80, 220, 600, 800, 1000), 0, (16, 18, 19), 0.030852),
    Position(Type.SPECIAL, "Free Parking", Group.NONE, 0, 0, 0, None, 0, (), 0.028836),
    Position(Type.PROPERTY, "Kentucky Avenue", Group.RED, 3, 220, 150, Rents(18, 90, 250, 700, 875, 1050), 0, (21, 23, 24), 0.028358),
    Position(Type.CHANCE, "Chance", Group.NONE, 0, 0, 0, None, 0, (), 0.010480),
    Position(Type.PROPERTY, "Indiana Avenue", Group.RED, 3, 220, 150, Rents(18, 90, 250, 700, 875, 1050), 0, (21, 23, 24), 0.027357),
    Position(Type.PROPERTY, "Illinois Avenue", Group.RED, 3, 240, 150, Rents(20, 100, 300, 750, 925, 1100), 0, (21, 23, 24), 0.031858),
    Position(Type.RAILROAD, "B&O Railroad", Group.RAILROAD, 4, 200, 0, None, 0, (5, 15, 25, 35), 0.030659),
    Position(Type.PROPERTY, "Atlantic Avenue", Group.YELLOW, 3, 260, 150, Rents(22, 110, 330, 800, 975, 1150), 0, (26, 27, 29), 0.027072),
    Position(Type.PROPERTY, "Ventnor Avenue", Group.YELLOW, 3, 260, 150, Rents(22, 110, 330, 800, 975, 1150), 0, (26, 27, 29), 0.026789),
    Position(Type.UTILITY, "Water Works", Group.UTILITY, 2, 150, 0, None, 0, (12, 28), 0.028074),
    Position(Type.PROPERTY, "Marvin Gardens", Group.YELLOW, 3, 280, 150, Rents(24, 120, 360, 850, 1025, 1200), 0, (26, 27, 29), 0.025861),
    Position(Type.SPECIAL, "Go to Jail", Group.NONE, 0, 0, 0, None, 0, (), 0.0000),
    Position(Type.PROPERTY, "Pacific Avenue", Group.GREEN, 3, 300, 200, Rents(26, 130, 390, 900, 110, 1275), 0, (31, 32, 34), 0.026774),
    Position(Type.PROPERTY, "North Carolina Avenue", Group.GREEN, 3, 300, 200, Rents(26, 130, 390, 900, 110, 1275), 0, (31, 32, 34), 0.026252),
    Position(Type.COMMUNITY, "Community Chest", Group.NONE, 0, 0, 0, None, 0, (), 0.023661),
    Position(Type.PROPERTY, "Pennsylvania Avenue", Group.GREEN, 3, 320, 200, Rents(28, 150, 450, 1000, 1200, 1400), 0, (31, 32, 34), 0.025006),
    Position(Type.RAILROAD, "Short Line", Group.RAILROAD, 4, 200, 0, None, 0, (5, 15, 25, 35), 0.024326),
    Position(Type.CHANCE, "Chance", Group.NONE, 0, 0, 0, None, 0, (), 0.008669),
    Position(Type.PROPERTY, "Park Place", Group.DARK_BLUE, 2, 350, 200, Rents(35, 175, 500, 1100, 1300, 1500), 0, (37, 39), 0.021864),
    Position(Type.SPECIAL, "Luxury Tax", Group.NONE, 0, 0, 0, None, 100, (), 0.021799),
    Position(Type.PROPERTY, "Boardwalk", Group.DARK_BLUE, 2, 400, 200, Rents(50, 200, 600, 1400, 1700, 2000), 0, (37, 39), 0.026260)
]

groups = [tuple([index for index, pos in enumerate(board) if pos.group == i]) for i in range(0, 10)]
