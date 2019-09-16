# Assignment 1
Some notes to understand code in assignment 1.

## Assignment requirements
1. `config.cpp`: Command line arg parsing, dependence on `config.h`
2. `easybj.h` / `easybj.cpp`: Logic for easy blackjack
3. `player.cpp`: Player logic, dependence on `player.h`

Both `main.cpp` and `shoe.h` / `shoe.cpp` do not need to be modified.

### Setup of WSL
+ `sudo apt install build-essential` to install other build essential tools including `make`

### Notes on `config.cpp`
+ What is `Config::process_arguments` as a function?
+ Is a `Config` object being instantiated here?
+ Why can `player` and `shoe` variables be called in the destructor? Is it an attribute of `Config`?

#### Observations
1. `usage` is the help function, no need to modify. Call `usage(argv[0])` when need to invoke.
2. Headers invoked include `config.h`, `player.h`, `shoe.h`, as well as other libraries:
    + `cstdio` for [C-style I/O](https://en.cppreference.com/w/cpp/header/cstdio)
    + `cstring` for [C-style null-terminated strings](https://en.cppreference.com/w/cpp/header/cstring)
    + `unistd` (UNIX standard library) for POSIX values and functions, link to [definitions](https://pubs.opengroup.org/onlinepubs/7908799/xsh/unistd.h.html), defined on POSIX systems only??? Seems like changing to `<unistd.h>` works. Only required if using `getopt`

Remember to check equality of strings using `strcmp` instead of `==`, the latter checks for pointer equality.

### Notes on `easybj.cpp`
Write here!

### Notes on `player.cpp`
Write here!
