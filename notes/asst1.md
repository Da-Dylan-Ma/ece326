# Assignment 1

## Assignment requirements
Edit the following files, according to specification on the [assignment page](http://fs.csl.toronto.edu/~sunk/asst1.html):
1. `config.cpp`: Command line arg parsing, dependence on `config.h`
2. `easybj.h` / `easybj.cpp`: Logic for easy blackjack
3. `player.cpp`: Player logic, dependence on `player.h`

Both `main.cpp` and `shoe.h` / `shoe.cpp` do not need to be modified.

### Notes
1. `usage` is the help function, no need to modify. Call `usage(argv[0])` when need to invoke.
2. Headers invoked include `config.h`, `player.h`, `shoe.h`, as well as other libraries:
    + `cstdio` for [C-style I/O](https://en.cppreference.com/w/cpp/header/cstdio)
    + `cstring` for [C-style null-terminated strings](https://en.cppreference.com/w/cpp/header/cstring)
    + `unistd` (UNIX standard library) for POSIX values and functions, link to [definitions](https://pubs.opengroup.org/onlinepubs/7908799/xsh/unistd.h.html), defined on POSIX systems only??? Seems like changing to `<unistd.h>` works. Only required if using `getopt`
3. Remember to check equality of strings using `strcmp` instead of `==`, the latter checks for pointer equality.
4. Factory building pattern: "Define an interface for creating an object, but let subclasses decide which class to instantiate. The Factory method lets a class defer instantiation it uses to subclasses."
    + Creating an object often requires complex processes not appropriate to include within a composing object. The object's creation may lead to a significant duplication of code, may require information not accessible to the composing object, may not provide a sufficient level of abstraction, or may otherwise not be part of the composing object's concerns.
    + The factory method design pattern handles these problems by defining a separate method for creating the objects, which subclasses can then override to specify the derived type of product that will be created.
    + Read up on the factory pattern [here](https://stackoverflow.com/questions/5120768/how-to-implement-the-factory-method-pattern-in-c-correctly).
5. Windows Subsystem for Linus setup: `sudo apt install build-essential` to install other build essential tools including `make`
6. Why do some classes possess the `factory` method? When is it called, or is it a special method handled differently by C++? Note that it is defined in the header file as a static method.
    + Answer: Called in the Config class when processing the arguments.
7. `Player::play(Hand*, Hand*)` is called to allow user to perform Blackjack actions. Suppose hit is called, but the `Shoe` object is not exposed to the `Player` to draw cards. A possible solution is to process everything in `Blackjack` which has access to `Shoe`, but how should `Player` pass the action to be taken to `Blackjack`, when the header of `Player` is fixed?
    + Can additional attributes and methods be assigned to `Player` in the implementation, despite not defined in the header?
    + Actually, the reference to Shoe can be passed to `Hand` class, since the definition is user-defined. This means the `Hand` class is excessively powerful though...

---

## Summary of initial code and tasks

### Compilation (headers)
1. `easybj.h`:
    + Declares `Player`, `Shoe`, `Config`, `Hand`, `Blackjack` classes
    + ***TODO***: Definition of const `Blackjack::dealer_hand`
    + ***TODO***: Declare other methods of `Blackjack` (if required)
    + ***TODO***: Definition of Hand class
2. `config.h`:
    + Declares `Player`, `Shoe` classes and `Config` struct
3. `player.h`:
    + Declares `Hand`, `Config`, `Player` classes
4. `shoe.h`:
    + Declares `Config`, `Shoe` classes

### Compilation (sources)
1. `config.cpp`:
    + Defines `~Config`
    + ***TODO***: Definition of `Config::process_arguments`
    + ***TODO***: Store game configuration data in `Config`
2. `shoe.cpp`:
    + Defines `InfiniteShoe` class
    + Defines `FileShoe` class
    + Defines `Shoe::factory`
3. `player.cpp`:
    + ***TODO***: Definition of `Player::factory`
    + ***TODO***: Definition of `Player::play`
    + ***TODO***: Definition of `Player::again`
    + ***TODO***: Definition of `Player::~Player`
4. `easybj.cpp`:
    + Defines `to_currency`
    + ***TODO***: Definition of `Blackjack::Blackjack`
    + ***TODO***: Definition of `Blackjack::~Blackjack`
    + ***TODO***: Definition of `Blackjack::start`
    + ***TODO***: Definition of `Blackjack::next`
    + ***TODO***: Definition of `Blackjack` string representation
    + ***TODO***: Definition of `Blackjack::finish`

---

## Program overview

### Main function
1. Instantiates `Config` with default arguments
2. Calls `Config::process_arguments` to parse arguments and save in `config`
3. Check if `Shoe::over` repeatedly
    1. Instantiates `Blackjack` with `Player` and `Shoe` in `config`
    2. Creates player hand using `Blackjack::start`
    3. Creates dealer hand using `Blackjack::dealer_hand`
    4. Check if player hand exists repeatedly
        1. Call `Player::play`
        2. Update player hand with `Blackjack::next`
    5. Call `Blackjack::finish`
    6. Print `Blackjack` string repr if required
    7. If `Player::again` returns true, repeat from step 3, else break
4. Print summary of game

### `Shoe -> (InfiniteShoe, FileShoe)` class
Defines the stack of cards from which both the dealer and player draws from. `InfiniteShoe` distributes cards from an infinite deck, while `FileShoe` distributes cards in a predetermined order specified from a file. Note that `CUT_DEPTH = 26` is defined, i.e. the number of cards remaining in the shoe before the dealer stops dealing cards from it to disincentivise card counting strategies.

```cpp
Shoe * factory(const Config * config)
// Generates InfiniteShoe or FileShoe based on parameters in Config

char pop() override;
// Returns a char from {'A', '2', ..., '9', 'T', 'J', 'Q', 'K'}

bool over() const;
// Checks if cut depth exceeded
```

### Utility functions
To be defined in `easybj.cpp`.

```cpp
// Converts card to value, 'A' == 1
int card_value(char card) {
    switch (card) {
        case 'A':
            return 1;
        case 'T':
        case 'J':
        case 'Q':
        case 'K':
            return 10;
        default:
            return stoi(card, nullptr, 10);
    }
    return -1; // error
}
```

### `Hand` class

The class is required to represent a hand in blackjack, to be defined in `easybj.h` and implemented in `easybj.cpp`. Since player cannot track hands, `Hand` should store split information and `Blackjack` will check. This is becoming very very non-OOP though...

```cpp
Player* player; // pointer to created Player stored in Config
Shoe* shoe; // pointer to created Shoe stored in Config
vector<char> cards; // list of cards in hand
double bet; // default 1.0, bet involved with hand
bool action_taken; // default false
bool action_allowed; // default true, false when stand
char split_card; // if not 0, the card to be split into new hand
bool can_player_split; // false if player has too many cards, disable_split()

// initialize
Hand(Player* p, Shoe* s):
    player(p), shoe(s), bet(1.0),
    action_taken(false), action_allowed(true),
    split_card(0), player_can_split(true) {}

Hand(Player* p, Shoe* s, char card_from_split):
    player(p), shoe(s), bet(1.0),
    action_taken(true), action_allowed(card_from_split == 'A'),
    split_card(0), player_can_split(true) {}


/*------ QUERIES ------*/

// Checks if hand is blackjack
bool is_blackjack() const {
    if (this.get_num_cards() != 2) return false;
    return get_hand_value() == 21;
}

bool is_bust() const {
    return get_hand_value_min() > 21;
}

// Checks if hand has an ace, easier to check
bool has_ace() const {
    for (char card: cards) {
        if (card == 'A') return true;
    }
    return false;
}

// Check possible actions, for printing and user input
bool can_play() const {
    return get_hand_value() < 21;
}

// Check if can double, i.e. two card hand
bool can_double() const {
    return get_num_cards() == 2;
}

// Check if action taken
bool can_surrender() const {
    return !action_taken;
}

// Check if can split, i.e. same value in two card hand
bool can_split() const {
    if (!this.can_player_split) return false;
    if (this.get_num_cards() != 2) return false;
    return card_value(cards[0]) == card_value(cards[1]);
}

std::ostream& operator<<(std::ostream& ostr, const Hand& hand) {
    // Print hand cards
    for (char card: hand.cards) ostr << card << " ";

    // Print value
    int hand_value = hand.get_hand_value();
    int hand_value_min = hand.get_hand_value_min();
    if (hand_value == 21) {
        if (hand_value_min == 21) {
            ostr << "(soft 21)";
        } else {
            ostr << "(hard 21)";
        }
    } else if (hand_value > 21) {
        ostr << "(bust)";
    } else {
        ostr << "(" << hand_value << ")";
    }

    // Print double
    if (hand.bet == 1.0*2) ostr << " DOUBLE";
    return ostr;
}


/*------ GETTERS ------*/

// Returns card if hand needs to be split, otherwise 0
char get_split_card() const { return split_card; }

// Get number of cards in hand, for double and split, i.e. cards.length
int get_num_cards() const { return cards.size(); }

// Get highest possible value of hand (under 21 if possible)
int get_hand_value() const {
    int value = this.get_hand_value_min();
    if ((value <= 11) && (this.has_ace())) {
        return value + 10;
    }
    return value;
}

// Get lowest possible value of hand, i.e. 'A' == 1
int get_hand_value_min() const {
    int value = 0;
    for (char card: cards) {
        value += card_value(card);
    }
    return value;
}


/*------ SETTERS ------*/

// Update hand, stand and surrender does nothing to Hand itself
// Add card to hand, using Shoe reference
// TODO: What about the case when shoe runs out of cards to supply?
void add_card() {
    cards.push_back(shoe.pop());
    action_taken = true;
}

// Disable splitting, called in Blackjack
void disable_split() {
    can_player_split = false;
}

// Stand
void call_stand() {
    action_allowed = false;
}

// Perform hit procedure
void call_hit() {
    add_card();
    action_allowed = get_hand_value_min() >= 21; // automatic stand at 21
}

// Perform doubling procedure
void call_double() {
    bet *= 2;
    call_hit();
}

// Returns new Hand with cards split
void call_split() {
    split_card = cards[0];
    // Rest of action performed in Blackjack
    // action_allowed = cards[0] != 'A'
    // Hand* other = new Hand(p, s, action_allowed);
    // this.add_card(); // which order?
    // other.add_card();
    // return other;
}

// Surrender
void call_surrender() {
    bet *= 0.5;
    call_stand();
}
```

### `Player` class

```cpp
double balance; // player profit
int nr_hands; // total number of hands played

// Follow Shoe::factory
// TODO: Code in automated playing, currently only manual mode supported.
Player* factory(const Config * config):
    balance(0.0), nr_hands(0) {}

// Dependent on definition of constructor
~Player() {}

// Returns player balance from all the games
double get_balance() const

// Returns number of hands played
int get_hands_played() const

// Update balance and number of hands fields
void update_balance(double val)

// Supposed to play player hand against the dealers
// Performs player subroutine, and manually assigning of cards to hands
// Assumption: Hand is playable
void play(Hand* hand, const Hand* dealer) {

    // Save possible actions
    bool can_double = hand.can_double();
    bool can_surrender = hand.can_surrender();
    bool can_split = hand.can_split();

    // REPL for manual user input
    while (true) {
        // Print command
        cout << "Stand (S) Hit (H)";
        if (can_double) cout << " Double (D)";
        if (can_surrender) cout << " Surrender (R)";
        if (can_split) cout << " Split (P)";
        cout << ": ";

        // Get user input
        string cmd; getline(cin, cmd);
        if (cmd.size() == 0) cmd = "a";
        switch (tolower(cmd[0])) {
            case 'h': return hand.call_hit();
            case 's': return hand.call_stand();
            case 'd': if (can_double) return hand.call_double();
            case 'r': if (can_surrender) return hand.call_surrender();
            case 'p': if (can_split) return hand.call_split();
            default: break;
        }
    }
}

// Returns boolean to determine if next game should be played, for manual input at the end of single game
bool again() const {
    cout << "Press Any Key to Continue, (Q to Quit): ";
    string cmd; getline(cin, cmd);
    if (cmd.size() != 0 && tolower(cmd[0]) == 'q') return false;
    return true;
}
```


### `Blackjack` class
Plays the blackjack game. Handles:
+ Logic of the game
+ Keeps track of player and dealer hands

```cpp
Player* player; // pointer to created Player stored in Config
Shoe* shoe; // pointer to created Shoe stored in Config
vector<Hand*> hands; // Keep track of hands available to be played
const Hand* dealer_hand_ptr; // Save dealer's hand
bool blackjack_found; // Quick terminate
double profit; // Total

// Constructor for a single Blackjack game
Blackjack(Player* p, Shoe* s):
    player(p), shoe(s), blackjack_found(false), profit(0.0) {

    dealer_hand_ptr = new Hand(p, s);
    dealer_hand_ptr.add_card();
    dealer_hand_ptr.add_card();
    if (dealer_hand_ptr->is_blackjack()) blackjack_found = true;

    Hand* player_hand = new Hand(p, s);
    player_hand.add_card();
    player_hand.add_card();
    if (player_hand->is_blackjack()) blackjack_found = true;

    hands.push_back(player_hand);
}

// Dependent on implementation of constructor
~Blackjack() {
    delete dealer_hand_ptr;
    for (Hand* hand: hands) delete hand;
}

// Return hand for dealer, or nullptr if game ended
const Hand* dealer_hand() const {
    if (blackjack_found) return nullptr;
    return dealer_hand_ptr;
}

// Returns the initial player hand, and start the game (?)
Hand* start() {
    if (blackjack_found) return nullptr;
    return hands[0];
}

// Returns the next hand the player can play
// Returns nullptr once the player subroutine ends
// This function may only be called after start(), and returns the next hand that the player can play. The return value may be nullptr if no more hands are left to be played. Note that if a hand has 21 points, it stands automatically.
Hand* next() {

    // Process hand splitting first
    for (int i = 0; i < hands.size(); i++) {
        char split_card = hands[i].get_split_card();
        if (split_card != 0) {
            Hand* new_hand_1 = new Hand(p, s, split_card);
            Hand* new_hand_2 = new Hand(p, s, split_card);
            new_hand_1.add_card();
            new_hand_2.add_card();

            hands.erase(hands.begin()+i); // insert at same position
            hands.insert(hands.begin()+i, new_hand_2);
            hands.insert(hands.begin()+i, new_hand_1);
        }
    }

    // Disable splitting if exceeded
    if (hands.size() == 4)
        for (Hand* hand: hands) hand.disable_split();
    }

    for (Hand* hand: hands) {
        if (hand.can_play()) return hand;
    }
    return nullptr;
}

// For string representation printing, not critical
// Do we need to print (blackjack) for blackjack case?
std::ostream& operator<<(std::ostream& ostr, const Blackjack& bj) {
    // Dealer results
    ostr << "Dealer: " << &bj.dealer_hand_ptr << endl;

    // Player results
    int hand_num = 1;
    for (Hand* hand: bj.hands) {
        ostr << "Hand " << hand_num++ <<": " << &hand << endl;
    }
    double result = bj.profit;
    ostr << "Result: " << (result < 0.0 ? "-$" : "$");
    ostr << std::fixed << std::setprecision(2) << result << endl;

    // Balance
    double bal = player->get_balance();
    ostr << "Current Balance: " << (bal < 0.0 ? "-$" : "$");
    ostr << std::fixed << std::setprecision(2) << bal << endl;
}

// Calculate profit earned by player and update `player->balance`
// This function may only be called after no more hands are left to be played. Its purpose is to allow the dealer to take action(s) and then updates the player's balance based on the outcome of the game. If the player has no live hands (i.e. all his/her hands busted or surrendered), then the dealer will not draw any cards. In all circumstances, you MUST call Player::update_balance exactly once during this function otherwise the number of hands played will be off.
void finish() {

    // Blackjack payoff
    if (blackjack_found) {
        Hand* player_hand = hands[0];
        if (player_hand->is_blackjack()) {
            player->update_balance(hand->bet * 1.5);
            profit += hand->bet * 1.5;
        } else if (dealer_hand_ptr->is_blackjack()) {
            player->update_balance(hand->bet * -1);
            profit += hand->bet * -1;
        } else {
            player->update_balance(0.0);
        }
        return;
    }

    // No blackjack payoff
    // Check if player is all bust, dealer will not draw cards in this case
    bool player_bust = true;
    for (Hand* hand: hands) {
        if (!hand->is_bust()) {
            player_bust = false;
            break;
        }
    }

    // Dealer actions
    if (player_bust) {
        while (true) {
            int dealer_value = dealer_hand_ptr->get_hand_value_min();
            if (dealer_value == 7 && dealer_hand_ptr->has_ace()) {
                dealer_hand_ptr->call_hit();
                continue;
            }
            dealer_value = dealer_hand_ptr->get_hand_value();
            if (dealer_value < 17) {
                dealer_hand_ptr->call_hit();
            } else {
                dealer_hand_ptr->call_stand();
                break;
            }
        }
    }

    // Calculate profit
    if (dealer_hand_ptr->is_bust()) {
        for (Hand* hand: hands) {
            if (hand->is_bust()) {
                player->update_balance(0.0);
            } else {
                player->update_balance(hand->bet);
                profit += hand->bet;
            }
        }
    } else {
        int dealer_value = dealer_hand_ptr->get_hand_value();
        for (Hand* hand: hands) {
            hand_value = hand->get_hand_value();
            if (hand_value < dealer_value || hand->is_bust()) {
                player->update_balance(hand->bet * -1);
                profit += hand->bet * -1;
            } else if (hand_value > dealer_value) {
                player->update_balance(hand->bet);
                profit += hand->bet;
            } else {
                player->update_balance(0.0);
            }
        }
    }
}

```

### `Config` class
`Config` stores all game setup information and process_arguments method declaration, as seen in the attributes below

```cpp
Player * player; // pointer to created Player
Shoe * shoe; // pointer to created Shoe
const char * strategy_file; // filepath to player strategy table
const char * shoe_file; // filepath to open FileShoe
const char * record_file; // filepath to save cards drawn from InfiniteShoe
long num_hands; // default 0, number of hands played in auto
long random_seed; // default -1, seed for InfiniteShoe
bool silent; // default false, silent mode to stop printing

// Accepts command line args, modify relevant fields
// Already detailed in config.cpp
int process_arguments(int argc, const char * argv[])
```

---

## Logic flowchart
### Starting configuration
```
1. Deal cards: dealer gets two, player gets two
2. Check blackjack:
    + If player BJ, player wins 1.5x bet [EXIT]
    + If dealer BJ, player loses bet [EXIT]
    + If both BJ, [EXIT]
```

### Player subroutine
```
1. Check available actions:
    + If no action taken, surrender allowed
    + If two-card hand, double allowed
    + If same value in two-card hand, split allowed
2. Get user input
    + Stand (S)
        1. GOTO DEALER SUBROUTINE
    + Hit (H)
        1. Add card to hand
        2. If 'A' == 1 and exceed 21, player loses bet [EXIT]
        3. If value == 21, GOTO PLAYER STAND
        3. GOTO PLAYER SUBROUTINE
    + Double (D)
        1. Increase bet to 2x
        2. GOTO PLAYER HIT
    + Surrender (R)
        1. Player loses 0.5x bet [EXIT]
    + Split (P)
        1. If both 'A':
            1. Create two separate hands
            2. Draw for each hand
            3. GOTO DEALER SUBROUTINE
        2. Create two separate hands
        3. Draw for each hand
        4. GOTO PLAYER SUBROUTINE
```

### Dealer subroutine
```
1. Sum value, with all 'A' == 1
2. If 'A' exist and value == 7 (soft 17), GOTO DEALER HIT
4. If sum <= 11 and 'A' exists, value add 10
5. If value < 17, GOTO DEALER HIT
6. GOTO DEALER STAND (includes hard 17)

+ HIT
    1. Add card to hand
    2. If 'A' == 1 and exceed 21, GOTO GAME FINISH
    3. GOTO TO DEALER SUBROUTINE
+ STAND
    1. GOTO GAME FINISH
```

### Game finish
Note that player is not bust, but dealer may be bust.
```
1. Calculate hand values for dealer and player:
    1. 'A' == 1, sum
    2. If sum <= 11 and 'A' exists, add 10
2. If dealer bust, all player (live) hands win bet [EXIT]
3. Compare values:
    + If player > dealer, player win bet [EXIT]
    + If player < dealer, player lose bet [EXIT]
```
