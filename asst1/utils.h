#include <iostream>
#define MAXLINE 256
static char read_input() {
  char buf[MAXLINE + 1];
  if (std::cin.getline(buf, MAXLINE)) {
    return buf[0];
  }
  return 0;
}
