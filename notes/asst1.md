# Assignment 1

## Assignment requirements
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

Remember to check equality of strings using `strcmp` instead of `==`, the latter checks for pointer equality.


---

## Function flowchart
#### Overview
+ Specify here how each function interacts with classes

---

## Program flowchart
### Compilation (headers)
1. `easybj.h`:
    + Declares `Player`, `Shoe`, `Config`, `Hand`, `Blackjack` classes
    + `Blackjack` declares main methods
    + ***TODO***: Definition of const `Blackjack::dealer_hand`
    + ***TODO***: Declare other methods of `Blackjack` (if required)
2. `config.h`:
    + Declares `Player`, `Shoe` classes and `Config` struct
    + `Config` stores all game setup information and `process_arguments` method declaration
3. `player.h`:
    + Declares `Hand`, `Config`, `Player` classes
    + `Player` stores money balance and games played information, requires `play`, `again`, `~Player` methods be defined, declares `Player::factory`
4. `shoe.h`:
    + Declares `Config`, `Shoe` classes
    + `Shoe` requires `~Shoe`, `pop`, `over` methods be defined, declares `Shoe::factory`

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

### Runtime
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

---

## Other notes

### Setup of WSL
+ `sudo apt install build-essential` to install other build essential tools including `make`
