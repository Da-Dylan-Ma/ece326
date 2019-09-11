 /*
 * config.h
 *
 * Config class definition
 *
 * Note: you may not change this file
 *
 * University of Toronto
 * Fall 2019
 */
 
#ifndef CONFIG_H
#define CONFIG_H

class Player;
class Shoe;

struct Config {
	Player * player;
	Shoe * shoe;
	const char * strategy_file;
	const char * shoe_file;
	const char * record_file;
	long num_hands;
	long random_seed;
	bool silent;
	
	Config() : player(nullptr), shoe(nullptr),
		strategy_file(nullptr), shoe_file(nullptr),
		record_file(nullptr), num_hands(0), 
		random_seed(-1), silent(false) {}
	~Config();
	
	/*
	 * Returns 0 on success, -1 otherwise
	 */
	int process_arguments(int argc, const char * argv[]);
};

#endif /* CONFIG_H */

