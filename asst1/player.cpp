/*
 * player.cpp
 *
 * Note: change this file to implement Player subclass
 *
 * University of Toronto
 * Fall 2019
 */

#include "player.h"
#include "easybj.h"
#include "config.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>



/****************************
**    UTILITY FUNCTIONS    **
****************************/

std::vector<std::string> split_whitespace(std::string line) {
	std::vector<std::string> tokens;
	std::istringstream iss(line);
	for (std::string s; iss >> s;)
		tokens.push_back(s);
	return tokens;
}



/***********************
**    MANUALPLAYER    **
***********************/

class ManualPlayer: public Player {
public:
	ManualPlayer(): Player(0) {}
	void play(Hand* hand, const Hand* dealer);
	bool again() const;
    void print_encounter(Hand* hand, const Hand* dealer) const;
};

void ManualPlayer::play(Hand* hand, const Hand* dealer) {
	print_encounter(hand, dealer);

    // Save possible actions
    bool can_double = hand->can_double();
    bool can_surrender = hand->can_surrender();
    bool can_split = hand->can_split();

    // REPL for manual user input
    while (true) {
        // Print command
        std::cout << "Stand (S) Hit (H)";
        if (can_double) std::cout << " Double (D)";
		if (can_split) std::cout << " Split (P)";
        if (can_surrender) std::cout << " Surrender (R)";
        std::cout << ": ";

        // Get user input
        std::string cmd; std::getline(std::cin, cmd);
        if (cmd.length() == 0) cmd = "a"; // placeholder
        switch (std::tolower(cmd[0])) {
            case 'h': { hand->call_hit(); return; }
            case 's': { hand->call_stand(); return; }
            case 'd': if (can_double) { hand->call_double(); return; } break;
            case 'r': if (can_surrender) { hand->call_surrender(); return; } break;
            case 'p': if (can_split) { hand->call_split(); return; } break;
            default: break;
        }
    }
}

bool ManualPlayer::again() const {
    std::cout << "Press Any Key to Continue, (Q to Quit): ";
    std::string cmd; std::getline(std::cin, cmd);
    if (cmd.size() != 0 && tolower(cmd[0]) == 'q') return false;
    return true;
}

void ManualPlayer::print_encounter(Hand* hand, const Hand* dealer) const {
    std::cout << "Dealer: " << *dealer << std::endl;
    std::cout << "Player: " << *hand << std::endl;
}



/*********************
**    AUTOPLAYER    **
*********************/

class AutoPlayer: public Player {
	long num_hands;
	std::unordered_map<std::string, std::unordered_map<std::string, std::string>> strategy;
public:
	AutoPlayer(long nhands): Player(0), num_hands(nhands) {}
	void play(Hand* hand, const Hand* dealer);
	bool again() const;
	int open(const char* filename);
};

void AutoPlayer::play(Hand* hand, const Hand* dealer) {
	std::string action = strategy[hand->get_code(false)][dealer->get_code(true)];
	// For some obscure reason, disabling this debugging statement causes the program to not display an output!
	// std::cout << "Strategy chosen: " << action << " " << hand->get_code(false) << " " << dealer->get_code(true) << std::endl;
	// Inserting `std::cout << std::flush;` doesn't help either...
	char primary_action = action[0];
	switch (std::tolower(primary_action)) {
		case 'h': { hand->call_hit(); return; }
		case 's': { hand->call_stand(); return; }
		case 'd': if (hand->can_double()) { hand->call_double(); return; } break;
		case 'r': if (hand->can_surrender()) { hand->call_surrender(); return; } break;
		case 'p': if (hand->can_split()) { hand->call_split(); return; } break;
		default: break;
	}

	char secondary_action = action[1];
	switch (std::tolower(secondary_action)) {
		case 'h': { hand->call_hit(); return; }
		case 's': { hand->call_stand(); return; }
		default: break;
	}
}

bool AutoPlayer::again() const { return this->get_hands_played() < num_hands; }

// Populate strategy table
int AutoPlayer::open(const char* filename) {
	std::ifstream file(filename);
	if (file.fail()) return -1;

	std::string line; std::getline(file, line);
	std::vector<std::string> dcodes = split_whitespace(line);

	for (int i = 0; i < 35; i++) { // spare the extensibility talk
		std::getline(file, line);
		std::vector<std::string> pstrat = split_whitespace(line);
		std::string pcode = pstrat[0];
		for (unsigned int j = 0; j < dcodes.size(); j++)
			strategy[pcode][dcodes[j]] = pstrat[j+1];
	}
	// for (auto kv1: strategy)
	// 	for (auto kv2: kv1.second)
	// 		std::cout << "[" << kv1.first << "][" << kv2.first << "] = " << kv2.second << std::endl;
	return 0;
}

// virtual is used for late binding for subclasses, already defined in Player
Player* Player::factory(const Config * config) {
	ManualPlayer* player;
	if (config->strategy_file != nullptr) {
		AutoPlayer* player = new AutoPlayer(config->num_hands);
		if (player->open(config->strategy_file) < 0) {
			delete player;
			return nullptr;
		}
		return player;
	}
	player = new ManualPlayer();
	return player;
}
