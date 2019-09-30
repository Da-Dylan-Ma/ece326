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
#include <iostream>
#include <string>


class ManualPlayer: public Player {

public:
	ManualPlayer(double bal): Player(bal) {}
	void play(Hand* hand, const Hand* dealer);
	bool again() const;
};

// Supposed to play player hand against the dealers
// Performs player subroutine, and manually assigning of cards to hands
// Assumption: Hand is playable
void ManualPlayer::play(Hand* hand, const Hand* dealer) {

	(void) dealer; // defer execution

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
        if (cmd.size() == 0) cmd = "a";
        switch (std::tolower(cmd[0])) {
            case 'h': return hand->call_hit();
            case 's': return hand->call_stand();
            case 'd': if (can_double) return hand->call_double(); break;
            case 'r': if (can_surrender) return hand->call_surrender(); break;
            case 'p': if (can_split) return hand->call_split(); break;
            default: break;
        }
    }
}

// Returns boolean to determine if next game should be played, for manual input at the end of single game
bool ManualPlayer::again() const {
    std::cout << "Press Any Key to Continue, (Q to Quit): ";
    std::string cmd; std::getline(std::cin, cmd);
    if (cmd.size() != 0 && tolower(cmd[0]) == 'q') return false;
    return true;
}


// Only manual mode
// virtual is used for late binding for subclasses, already defined in Player
Player* Player::factory(const Config * config) {
	(void) config;
	return new ManualPlayer(0.0);
}
