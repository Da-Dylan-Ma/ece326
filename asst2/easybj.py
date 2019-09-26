#!/usr/bin/python3
#
# easybj.py
#
# Calculate optimal strategy for the game of Easy Blackjack
#

from table import Table
from collections import defaultdict

HARD_CODE =['4','5','6','7','8','9','10','11','12','13','14',
            '15','16','17','18','19','20'] # hard hand codes
SOFT_CODE = ['AA','A2','A3','A4','A5','A6','A7','A8','A9'] # soft hand codes
SPLIT_CODE = ['22','33','44','55','66','77','88','99','TT','AA'] # can split
NON_SPLIT_CODE = HARD_CODE + SOFT_CODE # cannot split
STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE # can stand
PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:] # strategy table y-labels
DEALER_CODE = HARD_CODE + SOFT_CODE[:6] # strategy table x-labels

# All possible starting hands (hard 4 is always 22, and hard 20 is always TT)
INITIAL_CODE = HARD_CODE[1:-1] + SPLIT_CODE + SOFT_CODE[1:] + ['BJ']

BUST = 0 # representation of busted hand
DISTINCT = ['A','2','3','4','5','6','7','8','9','T'] # distinct card values
NUM_FACES = 4 # number of cards with 10 points
NUM_RANKS = 13 # number of ranks in a French deck

def isclose(a, b=1., rel_tol=1e-09, abs_tol=0.0):
    """ Returns whether a and b are close enough in floating point value """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def probability(card):
    """ Returns the probability of receiving this card """
    return (1 if card != 'T' else NUM_FACES) / NUM_RANKS

def card_value(card):
    """ Returns value of card, assuming 'A' == 1 """
    if card == "A": return 1
    if card == "T": return 10
    return int(card)

class Hand:
    """ Represents a Blackjack hand (owned by either player or dealer) """
    def __init__(self, x, y, dealer=False):
        self.cards = [x, y]
        self.is_dealer = dealer

    def probability(self):
        """ Returns the probability of receiving the hand as a float """
        p = 1.
        for c in self.cards:
            p *= probability(c)
        return p

    def code(self, nosplit=False):
        """ Returns the 'XX' code that represents the hand, 0 if busted
            nosplit: True if hand can split """
        # Note: self.cards may have more than 2 cards
        value = sum(map(card_value, self.cards))
        if len(self.cards) == 2:
            if self.cards[0] == self.cards[1]:
                if self.cards[0] == "A": return "AA" # special AA
                if not nosplit and not self.is_dealer:
                    return self.cards[0]*2 # split
            if value == 11 and "A" in self.cards: return "BJ" # blackjack

        if value > 21: return BUST # bust
        if value >= 11: return str(value) # hard
        if "A" in self.cards:
            if not self.is_dealer or value <= 7:
                return "A" + str(value-1) # soft
            return str(value+10) # dealer cannot hit > A6
        return str(value) # hard

class Calculator:
    """ Singleton class to store all the results. """

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

    def make_initial_cell(self, player, dealer):
        """ Populate initial probability table """
        table = self.initprob
        dc = dealer.code()
        pc = player.code()
        prob = dealer.probability() * player.probability()
        if table[pc,dc] is None:
            table[pc,dc] = prob
        else:
            table[pc,dc] += prob

    def make_initial_table(self):
        """ Initialize probability table """
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

    def verify_initial_table(self):
        """ Verify sum of initial table is close to 1 """
        total = 0.
        for x in self.initprob.xlabels:
            for y in self.initprob.ylabels:
                total += self.initprob[y,x]
        assert(isclose(total))

def calculate():
    """ Returns a dictionary containing all calculated ev tables and
        final strategy table """
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

if __name__ == "__main__":
    print(calculate())
