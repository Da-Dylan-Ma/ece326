#!/usr/bin/python3
#
# easybj.py
#
# Calculate optimal strategy for the game of Easy Blackjack
#

from table import Table
from collections import defaultdict

# code names for all the hard hands
HARD_CODE = [ '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
    '15', '16', '17', '18', '19', '20']

# code names for all the soft hands
SOFT_CODE = [ 'AA', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9' ]

# code names for all the hands that can be split
SPLIT_CODE = [ '22', '33', '44', '55', '66', '77', '88', '99', 'TT', 'AA' ]

# code names for all the hands that cannot be split
NON_SPLIT_CODE = HARD_CODE + SOFT_CODE

# code names for standing
STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE

# code names for all the y-labels in the strategy table
PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:]

# code names for all the x-labels in all the tables
DEALER_CODE = HARD_CODE + SOFT_CODE[:6]

# code names for all the initial player starting hands
# (hard 4 is always 22, and hard 20 is always TT)
INITIAL_CODE = HARD_CODE[1:-1] + SPLIT_CODE + SOFT_CODE[1:] + ['BJ']

#
# Returns whether a and b are close enough in floating point value
# Note: use this to debug your code
#
def isclose(a, b=1., rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# use the numeral value 0 to represent a busted hand (makes it easier to
# compare using integer comparison)
BUST = 0

# list of distinct card values
DISTINCT = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T' ]

# number of cards with 10 points
NUM_FACES = 4

# number of ranks in a French deck
NUM_RANKS = 13

# return the probability of receiving this card
def probability(card):
    return (1 if card != 'T' else NUM_FACES) / NUM_RANKS

def card_value(card):
    """ Returns value of card, assuming 'A' == 1 """
    if card == "A": return 1
    if card == "T": return 10
    return int(card)

#
# Represents a Blackjack hand (owned by either player or dealer)
#
# Note: you should make BIG changes to this class
#
class Hand:
    def __init__(self, x, y, dealer=False):
        self.cards = [x, y]
        self.is_dealer = dealer

    # probability of receiving this hand
    def probability(self):
        p = 1.
        for c in self.cards:
            p *= probability(c)
        return p

    # the code which represents this hand
    # assuming nosplit means the hand cannot split
    def code(self, nosplit=False):
        # assuming self.cards may have more than 2 cards, bust == hard value
        value = sum(map(card_value, self.cards))

        if len(self.cards) == 2:
            if self.cards[0] == self.cards[1]:
                if not nosplit or self.cards[0] == "A":
                    return self.cards[0]*2 # split hands
            if value == 11: return "BJ" # blackjack

        if value >= 11: return str(value) # hard
        if "A" in self.cards: return "A" + str(value-1) # soft
        return str(value) # hard

#
# Singleton class to store all the results.
#
# Note: you should make HUGE changes to this class
#
class Calculator:
    def __init__(self):
        self.initprob = Table(float, DEALER_CODE + ['BJ'], INITIAL_CODE, unit='%')
        self.dealprob = defaultdict(dict)
        self.stand_ev = Table(float, DEALER_CODE, STAND_CODE)
        self.hit_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.double_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.split_ev = Table(float, DEALER_CODE, SPLIT_CODE)
        self.optimal_ev = Table(float, DEALER_CODE, PLAYER_CODE)
        self.strategy = Table(str, DEALER_CODE, PLAYER_CODE)
        self.advantage = 0.

    # make each cell of the initial probability table
    def make_initial_cell(self, player, dealer):
        table = self.initprob
        dc = dealer.code()
        pc = player.code()
        prob = dealer.probability() * player.probability()
        if table[pc,dc] is None:
            table[pc,dc] = prob
        else:
            table[pc,dc] += prob

    # make the initial probability table
    def make_initial_table(self):
        #
        # TODO: refactor so that other table building functions can use it
        #
        for i in DISTINCT:
            for j in DISTINCT:
                for x in DISTINCT:
                    for y in DISTINCT:
                        dealer = Hand(i, j, dealer=True)
                        player = Hand(x, y)
                        self.make_initial_cell(player, dealer)

    # verify sum of initial table is close to 1
    def verify_initial_table(self):
        total = 0.
        for x in self.initprob.xlabels:
            for y in self.initprob.ylabels:
                total += self.initprob[y,x]
        assert(isclose(total))

#
# Calculate all the ev tables and the final strategy table and return them
# all in a dictionary
#
def calculate():
    calc = Calculator()

    calc.make_initial_table()

    # TODO: uncomment once you finished your table implementation
    #       and Hand.code implementation
    #calc.verify_initial_table()

    # TODO: calculate all other tables and numbers

    return {
        'initial' : calc.initprob,
        'dealer' : calc.dealprob,
        'stand' : calc.stand_ev,
        'hit' : calc.hit_ev,
        'double' : calc.double_ev,
        'split' : calc.split_ev,
        'optimal' : calc.optimal_ev,
        'strategy' : calc.strategy,
        'advantage' : calc.advantage,
    }
