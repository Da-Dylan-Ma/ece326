/*
 * config.cpp
 *
 * Parses program arguments and returns Config object
 *
 * Note: change this file to parse program arguments
 *
 * University of Toronto
 * Fall 2019
 */
#include "config.h"
#include <cctype>
#include "player.h"
#include "shoe.h"
#include <cstdio>
#include <cstring>
#include <unistd.h> // <unistd> original
#include <set>
#include <iostream>

static int
usage(const char * prog) {
  fprintf(stderr, "usage: %s [-h] [-f FILE|-i SEED [-r FILE]] [[-s] -a FILE NUM]\n", prog);
  fprintf(stderr, "Options:\n");
  fprintf(stderr, " -h:\tDisplay this message\n");
  fprintf(stderr, " -f:\tUse file-based shoe\n");
  fprintf(stderr, " -i:\tUse random-based shoe (default)\n");
  fprintf(stderr, " -r:\tRecord random-based shoe to file\n");
  fprintf(stderr, " -a:\tPlay automatically using strategy chart\n");
  fprintf(stderr, " -s:\tSilent mode\n");
  fprintf(stderr, " FILE:\tFile name for associated option\n");
  fprintf(stderr, " SEED:\trandom seed\n");
  fprintf(stderr, " NUM:\tnumber of hands to be played\n");
  return -1;
}

static bool is_option(const char* arg) {
  if (!arg) {
    return false;
  }
  return strlen(arg) == 2 && arg[0] == '-' && isalpha(arg[1]);
}


extern char *optarg;
extern int optind;
extern int opterr;
extern int optopt;

int
Config::process_arguments(int argc, const char * argv[])
{
  if (argc == 2 && !strcmp(argv[1], "-h")) {
    return usage(argv[0]);
  }
  std::set<int> parsed{};
  long num;
  int result;
  char* p_end;
  optind = 1;
  while( (result = getopt(argc, (char * const* )argv, ":f:i:r:a:sh")) != -1 ) {
    if (parsed.find(result) != parsed.end()) {
      fprintf(stderr, "Error: too many -%c options specified.\n", result);
      return -1;
    }
    if (is_option(optarg)) {
      fprintf(stderr, "%s: option requires an argument -- \'%c\'\n", argv[0], result);
      return -1;
    }
    switch (result) {
      case 'f':
        if (parsed.find((int)'i') != parsed.end()) {
          std::cerr << "Error: cannot choose both file and random-based shoe." << std::endl;
          return -1;
        }
        this->shoe_file = optarg;
        break;
      case 'i': {
        if (parsed.find((int) 'f') != parsed.end()) {
          std::cerr << "Error: cannot choose both file and random-based shoe." << std::endl;
          return -1;
        }
        num = strtol(optarg, &p_end, 0);
        if (num < 0 || (*p_end)) {
          std::cerr << "Error: SEED must be a non-negative integer." << std::endl;
          return -1;
        }
        this->random_seed = num;
        break;
      }
      case 'r':
        if (parsed.find((int) 'f') != parsed.end()) {
          std::cerr << "Error: recording is only available for random-based shoe." << std::endl;
          return -1;
        }
        this->record_file = optarg;
        break;
      case 'a':
        //-a has two arguments here, so we must do something special
        if (optind == argc && is_option(argv[optind - 1])) {
          fprintf(stderr, "%s: option requires an argument -- \'%c\'\n", argv[0], result);
          return -1;
        } else if (optind == argc) {
          if (is_option(argv[optind - 1]) || !isdigit(argv[optind - 1][0])) {
            std::cerr << "Error: must specify number of hands when playing automatically." << std::endl;
            return -1;
          } 
        }
        if (is_option(argv[optind]) || isalpha(argv[optind][0])) {
		std::cerr << "we are here 5" << std::endl;
          std::cerr << "Error: must specify number of hands when playing automatically." << std::endl;
          return -1;
        }
        num = strtol(argv[optind], &p_end, 0);
        if (num <= 0 || (*p_end)) {
          std::cerr << "Error: NUM must be a natural number." << std::endl;
          return -1;
        }
        this->strategy_file = argv[optind - 1];
        this->num_hands = num;
        //if all things are right, optind is now point to second argument of -a
        //so we must add it manually to point to the next option.
        optind++;
        break;
      case 'h':
        return usage(argv[0]);
      case 's':
        break;
      case ':':
        fprintf(stderr, "%s: option requires an argument -- \'%c\'\n", argv[0], optopt);
        return -1;
      case '?':
        fprintf(stderr, "%s, invalid option -- \'%c\'\n", argv[0], optopt);
        return -1;
      default:
        return usage(argv[0]);
    }
    if (result && isalpha(result)) {
      parsed.insert(result);
    }
  }
  if (parsed.find((int)'s') != parsed.end() ) {
    if (parsed.find((int)'a') == parsed.end()) {
      std::cerr << "Error: silent mode is only available when playing automatically." << std::endl;
      return -1;
    } else {
      silent = true;
    }
  }
  player = Player::factory(this);
  if (player == nullptr) {
    fprintf(stderr, "Error: cannot instantiate Player. (bad file?)\n");
    return usage(argv[0]);
  }

  shoe = Shoe::factory(this);
  if (shoe == nullptr) {
    fprintf(stderr, "Error: cannot instantiate Shoe. (bad file?)\n");
    return usage(argv[0]);
  }

  return 0;
}

Config::~Config()
{
  if (player != nullptr) {
    delete player;
    player = nullptr;
  }

  if (shoe != nullptr) {
    delete shoe;
    shoe = nullptr;
  }

}
