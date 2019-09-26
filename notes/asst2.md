# Assignment 2

## Assignment requirements

1. Modify `table.py` to complete implementation. (done)
2. Complete `Hand.code()` to return the hand representation. (done)
3. Generate dealer/player tables:
    + Calculate dealer table.
    + Calculate player stand table.
    + Calculate player hit/double table.
    + Calculate player split table.
4. Generate strategy table based on optimal table calculations.
5. Calculate theoretical player advantage.

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

##### H19-H19
Accounting for the 1/13 probability of getting H20 with an ace,

| Player | Probability | Payoff |
|---|---|---|
| 21 | 1/13 + 1/13(1/13) | +14/169 |
| bust | 11/13 + 1/13(12/13) | -155/169 |
|| **HIT** | -141/169 |
|| **STAND** | **0** |

As a reminder, according to the assignment, it is not as straightforward as knowing that H20-H19 calls for a stand, and hence H20 will have the payoff +1/13. The base cases for stopping recursion for hitting are *only 21 and busting alone*. That means the table below is supposedly bogus:

| Player | Probability | Payoff |
|---|---|---|
| 20 | 1/13 | +1/13 |
| 21 | 1/13 | +1/13 |
| bust | 11/13 | -11/13 |
|| **HIT** | -9/13 |
|| **STAND** | **0** |

It is nonsense probabilistically, but it has some merits from a programming perspective to minimize complexity.

##### H18-H19
Accounting for the probability of obtaining 21 from both H20-H19 and H19-H19,

| Player | Probability | Payoff |
|---|---|---|
| 21 | 1/13 + 1/13(1/13) + 1/13(14/169) | +196/2197 |
| bust | 10/13 + 1/13(12/13) + 1/13(155/169) | -2001/2197 |
|| **HIT** | **-1805/2197** |
|| **STAND** | -1 |

##### Fitting H17-H19 together
Again, we ignore all the payoffs and only assume 21 is the target hand we want.

| Player | Probability | Payoff |
|---|---|---|
| 21 | 1/13 + 1/13(1/13) + 1/13(14/169) + 1/13(196/2197) | +2744/28561 |
| bust | 9/13 + 1/13(12/13) + 1/13(155/169) + 1/13(2001/2197) | -25817/28561 |
|| **HIT** | **-23073/28561** |
|| **STAND** | -1 |

---

## Implementation



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
