#!/usr/bin/python3
#
# easybj.py
#
# Calculate optimal strategy for the game of Easy Blackjack
#

from table import Table
from collections import defaultdict
import timeit
import copy



###################
##   CONSTANTS   ##
###################

BUST_CODE = "00" # busted hand code
HARD_CODE = ['4','5','6','7','8','9','10','11','12','13','14',
             '15','16','17','18','19','20'] # hard hand codes
SOFT_CODE = ['AA','A2','A3','A4','A5','A6','A7','A8','A9'] # soft hand codes
SPLIT_CODE = ['22','33','44','55','66','77','88','99','TT','AA'] # can split
NON_SPLIT_CODE = HARD_CODE + SOFT_CODE # cannot split
STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE # can stand
PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:] # strategy table y-labels
DEALER_CODE = HARD_CODE + SOFT_CODE[:6] # strategy table x-labels

PLAYER_STAND_CODE = ["21", BUST_CODE]
DEALER_STAND_CODE = HARD_CODE[-4:] + PLAYER_STAND_CODE

# All possible starting hands (hard 4 is always 22, and hard 20 is always TT)
INITIAL_CODE = HARD_CODE[1:-1] + SPLIT_CODE + SOFT_CODE[1:] + ['BJ']

BUST = 0 # representation of busted hand
DISTINCT = ['A','2','3','4','5','6','7','8','9','T'] # distinct card values
NUM_FACES = 4 # number of cards with 10 points
NUM_RANKS = 13 # number of ranks in a French deck



###########################
##   UTILITY FUNCTIONS   ##
###########################

PERFORMANCE_DATA = ""

def profile(f):
    def wrapper(*args, **kwargs):
        global PERFORMANCE_DATA
        start_time = timeit.default_timer()
        result = f(*args, **kwargs)
        end_time = timeit.default_timer()
        tdelta = end_time - start_time
        PERFORMANCE_DATA += "\nINFO: {} ran in {:.3f} seconds.".format(f.__name__, tdelta)
    return wrapper

def code2score(code):
    """ Get score from code. """
    uniques = {"BJ":21, "21":21, "TT":20, "AA":12}
    if code in uniques: return uniques[code]
    if code in HARD_CODE: return int(code)
    if code in SOFT_CODE: return int(code[1])+11
    return 2*int(code[0]) # SPLIT_CODE

def code2cards(code):
    """ Get possible cards from code, avoiding collisions. """
    uniques = {"BJ":"AT", "21":"777", "20":"28T", "4":"4"}
    if code in uniques: return uniques[code]
    if code in HARD_CODE:
        return "2"+str(int(code)-2) if int(code) <= 11 else "T"+str(int(code)-10)
    return code # SOFT_CODE or SPLIT_CODE

def cards2code(cards, dealer=False, nosplit=False):
    if len(cards) == 2 and cards[0] == '0': return BUST_CODE
    return Hand(cards, dealer=dealer).code(nosplit=nosplit)

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



####################
##   HAND CLASS   ##
####################

class Hand:
    """ Represents a Blackjack hand (owned by either player or dealer) """

    def __init__(self, cards, dealer=False):
        """ cards: iterable of cards
            dealer: boolean, owner of hand is dealer """
        self.cards = list(cards)
        self.is_dealer = dealer

    def probability(self):
        """ Returns the probability of receiving the hand as a float """
        p = 1.
        for c in self.cards:
            p *= probability(c)
        return p

    def code(self, nosplit=False):
        """ Returns the 'XX' code that represents the hand, '00' if busted
            nosplit: True if hand can split """
        # Note: self.cards may have more than 2 cards
        value = sum(map(card_value, self.cards))
        if len(self.cards) == 2:
            if self.cards[0] == self.cards[1]:
                if self.cards[0] == "A": return "AA" # special AA
                if not nosplit and not self.is_dealer:
                    return self.cards[0]*2 # split
            if value == 11 and "A" in self.cards: return "BJ" # blackjack

        if value > 21: return BUST_CODE # bust
        if value > 11: return str(value) # hard, (A 4 6) -> 21
        if "A" in self.cards:
            if not self.is_dealer or value <= 7:
                if value == 11: return "21" # (A 9 A) -> 21
                return "A" + str(value-1) # soft
            return str(value+10) # dealer cannot hit > A6
        return str(value) # hard

    def value(self):
        """ Returns score of Hand, 0 if busted """
        value = sum(map(card_value, self.cards))
        if "A" in self.cards and value <= 11: return value + 10
        if value <= 21: return value
        return BUST



##########################
##   CALCULATOR CLASS   ##
##########################

class Calculator:
    """ Singleton class to store all the results. """

    def __init__(self):
        self.initprob = Table(float, DEALER_CODE + ['BJ'], INITIAL_CODE, unit='%')
        self.dealprob = defaultdict(lambda: defaultdict(lambda: 0)) # initialize 0
        self.stand_ev = Table(float, DEALER_CODE, STAND_CODE)
        self.hit_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.double_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.split_ev = Table(float, DEALER_CODE, SPLIT_CODE)
        self.optimal_ev = Table(float, DEALER_CODE, PLAYER_CODE)
        self.strategy = Table(str, DEALER_CODE, PLAYER_CODE)
        self.advantage = 0.
        self.resplit_ev = [
            Table(float, DEALER_CODE, STAND_CODE),
            Table(float, DEALER_CODE, SPLIT_CODE[:-1]),
            Table(float, DEALER_CODE, SPLIT_CODE[:-1]),
        ]


    #################################
    ##  INITIAL PROBABILITY TABLE  ##
    #################################

    def create_initial_cell(self, player, dealer):
        """ Populate cell in initial probability table """
        table = self.initprob
        dc = dealer.code()
        pc = player.code()
        prob = dealer.probability() * player.probability()
        if table[pc,dc] is None:
            table[pc,dc] = prob
        else:
            table[pc,dc] += prob

    @profile
    def create_initial_table(self):
        """ Initialize probability table """
        # TODO: refactor so that other table building functions can use it
        for i in DISTINCT:
            for j in DISTINCT:
                for x in DISTINCT:
                    for y in DISTINCT:
                        dealer = Hand([i, j], dealer=True)
                        player = Hand([x, y])
                        self.create_initial_cell(player, dealer)

    @profile
    def verify_initial_table(self):
        """ Verify sum of initial table is close to 1 """
        total = 0.
        for x in self.initprob.xlabels:
            for y in self.initprob.ylabels:
                total += self.initprob[y,x]
        assert(isclose(total))


    ################################
    ##  DEALER PROBABILITY TABLE  ##
    ################################

    @profile
    def create_dealer_table(self):
        """ Populate dealer table """
        table = self.dealprob
        # Add base cases for recursion termination
        for code in DEALER_STAND_CODE: table[code][code2score(code)] = 1.0
        for code in DEALER_CODE: self.get_dealer_prob(code) # memoization

        # Remove bust code
        del table[BUST_CODE]

    def get_dealer_prob(self, code):
        """ Returns probabilities of possible dealer outcomes """
        table = self.dealprob
        if code in table: return table[code]

        curr_prob = table[code]
        curr_prob = copy.deepcopy(table[code])
        for card in DISTINCT: # all possible draws
            cards = cards2code(code2cards(code)+card, dealer=True)
            next_prob = self.get_dealer_prob(cards) # assume probs exists
            for score, prob in next_prob.items():
                curr_prob[score] += probability(card)*next_prob[score]

        table[code] = curr_prob
        return curr_prob # return probabilities, for recursion

    @profile
    def verify_dealer_table(self):
        """ Assert sum of probabilities equal 1 """
        for probs in self.dealprob.values():
            assert(isclose(sum(probs.values())))


    ##########################
    ##  STAND PAYOFF TABLE  ##
    ##########################

    @profile
    def create_stand_table(self):
        """ Populate stand EV table """
        # Assuming dealer will ALWAYS hit when not at least hard 17
        # Uses dealer table probabilities
        table = self.stand_ev
        for code in STAND_CODE:
            player_score = code2score(code)
            for dealer_code in DEALER_CODE:
                payoff = 0.0
                for dealer_score, prob in self.dealprob[dealer_code].items():
                    if dealer_score == BUST or dealer_score < player_score:
                        payoff += prob
                    elif dealer_score > player_score:
                        payoff -= prob
                table[code, dealer_code] = payoff


    ########################
    ##  HIT PAYOFF TABLE  ##
    ########################

    @profile
    def create_hit_table(self):
        """ Populate hit EV table """
        self.middle = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        for code in NON_SPLIT_CODE:
            for dealer_code in DEALER_CODE:
                payoff = 0.0 # process a single hit first
                for card in DISTINCT: # all possible draws
                    next_code = cards2code(code2cards(code)+card, nosplit=True)
                    payoff += probability(card)*self.get_hit_outcome(next_code, dealer_code)
                self.hit_ev[code, dealer_code] = payoff

    def get_hit_outcome(self, code, dealer_code):
        table = self.middle
        if code == "21": return self.stand_ev["21", dealer_code]
        if code == BUST_CODE: return -1.0

        outcome = table[code, dealer_code] # memoization
        if outcome is not None: return outcome

        # Hit once, and determine outcome based on optimal outcome
        payoff = 0.0
        for card in DISTINCT: # all possible draws
            next_code = cards2code(code2cards(code)+card, nosplit=True)
            payoff += probability(card)*self.get_hit_outcome(next_code, dealer_code)

        outcome = max(self.stand_ev[code, dealer_code], payoff)
        table[code, dealer_code] = outcome
        return outcome


    ###########################
    ##  DOUBLE PAYOFF TABLE  ##
    ###########################

    @profile
    def create_double_table(self):
        """ Populate double EV table """
        # TODO: Merge with hit EV by multiplication of 2
        for code in NON_SPLIT_CODE:
            for dealer_code in DEALER_CODE:
                payoff = 0 # initial hit
                for card in DISTINCT:  # all possible draws
                    next_code = cards2code(code2cards(code)+card, nosplit=True)
                    payoff += probability(card)*self.get_double_outcome(next_code, dealer_code)
                self.double_ev[code, dealer_code] = payoff

    def get_double_outcome(self, code, dealer_code):
        if code == "21": return 2 * self.stand_ev["21", dealer_code]
        if code == BUST_CODE: return -2.0
        return 2 * self.stand_ev[code, dealer_code]


    ##########################
    ##  SPLIT PAYOFF TABLE  ##
    ##########################

    @profile
    def create_split_table(self):
        """ Populate split EV table """
        for code in SPLIT_CODE:
            for dealer_code in DEALER_CODE:
                self.get_split_outcome(code, dealer_code)

    def get_split_outcome(self, code, dealer_code):
        # find best between hits, doubles and splits
        table = self.split_ev
        split_card = code[0]
        payoff = 0.0
        # hit sequence
        for card in DISTINCT:
            next_code = cards2code(split_card+card, nosplit=True) # assume no split
            # how about when no more splits are allowed? need to account for that?
            # should split be accounted? will lead to infinite loop.
            # if no, then no special case for AA
            if next_code in ("21", "BJ"):
                payoff += probability(card)*self.stand_ev["21", dealer_code]
            elif next_code in BUST_CODE:
                payoff += probability(card)*-1
            else:
                payoff += probability(card)*max(self.stand_ev[next_code, dealer_code], self.hit_ev[next_code, dealer_code], self.double_ev[next_code, dealer_code])
        table[code, dealer_code] = payoff*2 # split hands has double chances
        return payoff*2


    ######################
    ##  OPTIMAL ACTION  ##
    ######################

    @profile
    def create_optimal_table(self):
        """ Populate optimal EV table and strategy """
        for code in PLAYER_CODE:
            for dealer_code in DEALER_CODE:
                evs = {"R": -0.5}
                tables = (self.stand_ev, self.hit_ev, self.double_ev, self.split_ev)
                actions = ("S", "H", "D", "P")
                for table, action in zip(tables, actions):
                    try:
                        evs[action] = table[code, dealer_code]
                    except KeyError:
                        try:
                            evs[action] = table[cards2code(code, nosplit=True), dealer_code] # stand/hit for split_codes
                        except:
                            pass # ignore non-valid accesses, i.e. non-valid action

                # best action
                opt_action, opt_ev = max(evs.items(), key=lambda kv: kv[1])
                if opt_action in ("D", "P", "R"):
                    opt_action += max(filter(lambda kv: kv[0] not in ("D", "P", "R"), evs.items()), key=lambda kv: kv[1])[0].lower()

                self.optimal_ev[code, dealer_code] = opt_ev
                self.strategy[code, dealer_code] = opt_action


    ########################
    ##  PLAYER ADVANTAGE  ##
    ########################

    @profile
    def calculate_player_advantage(self):
        for pc in INITIAL_CODE:
            for dc in DEALER_CODE + ["BJ"]:
                if dc == "BJ" and pc == "BJ": continue
                elif dc != "BJ" and pc == "BJ":
                    self.advantage += self.initprob[pc, dc] * 1.5
                elif dc == "BJ" and pc != "BJ":
                    self.advantage += self.initprob[pc, dc] * -1
                else:
                    self.advantage += self.initprob[pc, dc]\
                                    * self.optimal_ev[pc, dc]

def calculate():
    """ Returns a dictionary containing all calculated ev tables and
        final strategy table """

    calc = Calculator()

    calc.create_initial_table()
    calc.verify_initial_table()
    calc.create_dealer_table()
    calc.verify_dealer_table()
    calc.create_stand_table()
    calc.create_hit_table()
    calc.create_double_table()
    calc.create_split_table()
    calc.create_optimal_table()
    calc.calculate_player_advantage()


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
    result = calculate()
    initial = result["initial"]
    d = result["dealer"]
    s = result["stand"]
    h = result["hit"]
    db = result["double"]
    k = result["split"]
    o = result["optimal"]
    strategy = result["strategy"]
    a = result["advantage"]

    print(PERFORMANCE_DATA)
