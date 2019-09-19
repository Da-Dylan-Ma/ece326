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

---

## Summary of initial code and tasks

### Compilation (headers)
1. `easybj.h`:
    + Declares `Player`, `Shoe`, `Config`, `Hand`, `Blackjack` classes
    + ***TODO***: Definition of const `Blackjack::dealer_hand`
    + ***TODO***: Declare other methods of `Blackjack` (if required)
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

### `Hand` class

The class is required to represent a hand in blackjack. Should probably be implemented separately in `hand.cpp` as a principle of OOP. What attributes should it possess? Bet? Value?

### `Player` class
What should this class additionally do?

```cpp
double balance; // player profit
int nr_hands; // total number of hands played

Player * factory(const Config * config)
// TODO: Follow Shoe::factory

~Player()
// TODO: Dependent on definition of constructor

double get_balance() const
// Returns player balance from all the games

int get_hands_played() const
// Returns number of hands played

void update_balance(double val)
// Update balance and number of hands fields

void play(Hand * hand, const Hand * dealer)
// TODO: Supposed to play player hand against the dealer's

bool again() const
// TODO: Returns boolean to determine if next game should be played, for manual input
```

### `Blackjack` class
Plays the blackjack game. Handles:
+ Logic of the game
+ Keeps track of player and dealer hands

```cpp
Player * player; // pointer to created Player stored in Config
Shoe * shoe; // pointer to created Shoe stored in Config

Blackjack(Player * p, Shoe * s): player(p), shoe(s)
// TODO: Constructor for a single Blackjack game

~Blackjack()
// TODO: Dependent on implementation of constructor

Hand * start()
// TODO: Returns the initial player hand, and start the game (?)

Hand * next()
// TODO: Updates player hand

std::ostream & operator<<(std::ostream & ostr, const Blackjack & bj)
// TODO: For string representation printing, not critical

void finish()
// TODO: Calculate profit earned by player and update `player->balance`
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

int process_arguments(int argc, const char * argv[])
// TODO: Accepts command line args, modify relevant fields
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
