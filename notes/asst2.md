# Assignment 2

## Assignment requirements

1. Modify `table.py` to complete implementation. (done)
2. Complete `Hand.code()` to return the hand representation. (done)
3. Generate dealer/player tables:
    + Calculate dealer table. (done)
    + Calculate player stand table. (done)
    + Calculate player hit/double table.
    + Calculate player split table.
4. Generate strategy table based on optimal table calculations.
5. Calculate theoretical player advantage.

### Notes

+ Will the dealer hit in `H15-H16`, even though it is guaranteed a win?
+ Why is `H20-H19` not have a stand payoff of +1, since we know the behaviour of the dealer, i.e. will not hit? Is this strategy to calculate until 21/bust base cases truly the optimal strategy?

---

## Writeup

The choice of action in blackjack to take depends on the expected value (EV) or the payout of the action. Suppose the payoff (in $, player's perspective) with hard 19 vs dealer's hard 20 (denoted H19-H20) for each respective action is given by:

| Hit    | Double | Stand  | Surrender |
|--------|--------|--------|-----------|
| -0.768 | -1.538 | -1.000 | -0.500    |

The most optimal action (with the highest payoff) is to surrender.

#### Stand payoff

Note the assumptions:
+ Drawing from infinite shoe, i.e. P(card) = 1/13
+ Initial bet is $1
+ Dealer hits on hand with S17 or <17, and stands otherwise

The payoff for standing at H18-H15 is

| Dealer | Probability | Payoff |
|---|---|---|
| 17 | 1/13 | +1/13 |
| 18 | 1/13 | 0 |
| 19-21 | 3/13 | -3/13 |
| bust | 7/13 | +7/13 |
| ***16*** | ***1/13*** | ***?*** |

However, since the dealer will still hit on H16 with the payoff represented as:

| Dealer | Probability | Payoff |
|---|---|---|
| 17 | 1/13 | +1/13 |
| 18 | 1/13 | 0 |
| 19-21 | 3/13 | -3/13 |
| bust | 8/13 | +8/13 |

We can add the probabilities from this table and determine the H18-H15 payoff to be +0.420 since `F(H15) = F(H15|noAce) + P(Ace)*F(H16)`, i.e.

| Dealer | Probability | Payoff |
|---|---|---|
| 17 | 1/13 + 1/13(1/13) = 14/169 | +14/169 |
| 18 | 1/13 + 1/13(1/13) = 14/169 | 0 |
| 19-21 | 3/13 + 1/13(3/13) = 42/169 | -42/169 |
| bust | 7/13 + 1/13(8/13) = 99/169 | +99/169 |
| **TOTAL** | 1 | +71/169 |

The goal is to use previously calculated payoff tables (cached as part of dynamic programming) to determine the actual payoff at different hands. Careful calculation tells us that the sum of probabilities is equal to 1.

#### Hit payoff

I may have misunderstood what the calculation of the hit payoff involved.

The idea is likely to find the maximum payoff between hitting and standing, then assigning the payoff as the hit payoff for the encounter.
In other words,

```python
def create_hit_table(self):
    """ Populate hit EV table """
    for code in NON_SPLIT_CODE:
        for dealer_code in DEALER_CODE:
            self.get_hit_outcome(code, dealer_code)

def get_hit_outcome(self, code, dealer_code):
    table = self.hit_ev
    if code == "21": return self.stand_ev["21", dealer_code]
    if code == BUST_CODE: return -1.0

    outcome = table[code, dealer_code]
    if outcome != None: return outcome

    payoff = 0.0
    for card in DISTINCT: # all possible draws
        next_code = cards2code(code2cards(code)+card, nosplit=True)
        payoff += probability(card)*self.get_hit_outcome(next_code, dealer_code)

    outcome = max(self.stand_ev[code, dealer_code], payoff)
    table[code, dealer_code] = outcome
    return outcome
```

This is in contrast to the previously expounded idea of calculating the actual probabilities of getting 21 or bust, and comparing pairwise with the dealer probabilities, or:

```python
PLAYER_STAND_CODE = ["21", "00"]

def create_hit_table_deprec(self):
    """ Populate hit EV table """
    table = self.hit_ev
    for code in NON_SPLIT_CODE:
        for dealer_code in DEALER_CODE:
            player_probs = self.playerprob[code]
            dealer_probs = self.dealprob[dealer_code]

            payoff = 0.0
            for player_score, player_prob in player_probs.items():
                for dealer_score, dealer_prob in dealer_probs.items():
                    if player_score > dealer_score:
                        payoff += player_prob * dealer_prob
                    elif player_score < dealer_score:
                        payoff -= player_prob * dealer_prob
            table[code, dealer_code] = payoff
```

The hit payoff can be calculated once the stand payoff is calculated. Suppose we have H17-H19, and the square bracketed payoffs are unknown at the moment,

| Player | Probability | Payoff |
|---|---|---|
| 18 | 1/13 | ? |
| 19 | 1/13 | ? |
| 20 | 1/13 | ? |
| 21 | 1/13 | +1/13 |
| bust | 9/13 | -9/13 |
|| **HIT** | ? |
|| **STAND** | -1 |

In order to establish the payoff, we determine the hit *and* stand payoffs in each scenario, by calculating their probabilities, i.e.

##### H20-H19

| Player | Probability | Payoff |
|---|---|---|
| 21 | 1/13 | +1/13 |
| bust | 12/13 | -12/13 |
|| **HIT** | -11/13 |
|| **STAND** | **+1** |

We can then assign the *hit outcome* to be the maximum of those two, i.e. +1.
Memoization can be performed to obtain the maximum of hit vs stand payoff.
If the value is still unknown, we continue recursing until the probability for hit is -1, i.e. when 21 is reached, after which we obtain the result from the stand table because it will always have a higher payoff.

---

## Program overview

### main.py
Calls `easybj.calculate()`. As simple as that. The rest of the heavy-lifting is already done.

### table.py
Defines special `Table` class for exception handling when getting and setting data into a database. Underlying data structure has been implemented as a dictionary of dictionaries.

### easybj.py
```python
# Hand codes
HARD_CODE = ['4', ..., '20'] # hard hands
SOFT_CODE = ['AA', 'A2', ..., 'A9'] # soft hands
SPLIT_CODE = ['22', ..., '99', 'TT', 'AA'] # hands that can be split
NON_SPLIT_CODE # hands that cannot be split
STAND_CODE # all codes that allow standing
PLAYER_CODE # all possible player codes
DEALER_CODE # all possible dealer codes
INITIAL_CODE # all possible starting hands

# Card and hand values
BUST # bust hand value
DISTINCT # distinct card values
NUM_FACES # number of cards with 10 points
NUM_RANKS # numbers of ranks in a French deck

# Functions
isclose(a, b) # returns True if floating a == floating b
probability(card) # returns probability of getting a card
calculate() # returns dictionary of payoff tables and strategy table

Hand.__init__(self, x, y, dealer=False)
Hand.probability(self) # returns probability of getting Hand
Hand.code(self, nosplit=False) # returns the code representing the hand

Calculator.__init__(self) # stores results
Calculator.make_initial_cell(self, player, dealer) # populate initial probability table
Calculator.make_initial_table(self) # construct initial probability table
Calculator.verify_initial_table(self) # verify sum is 1
```
