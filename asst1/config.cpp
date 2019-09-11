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
#include "player.h"
#include "shoe.h"
#include <cstdio>
#include <cstring>

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

int
Config::process_arguments(int argc, const char * argv[])
{
    /*
     * TODO: implement this
     */
     
    if (argc == 2 && !strcmp(argv[1], "-h")) {
        return usage(argv[0]);
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
	if (player != nullptr)
		delete player;
	
	if (shoe != nullptr)
		delete shoe;
}

