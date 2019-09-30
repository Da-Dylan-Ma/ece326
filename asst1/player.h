/*
 * player.h
 *
 * Header file for Player base class
 *
 * Note: you may not change this file
 *
 * University of Toronto
 * Fall 2019
 */

#ifndef PLAYER_H
#define PLAYER_H

// forward declaration
class Hand;
class Config;

class Player {
	double balance;
	int nr_hands;

public:
	Player(double bal=0.) : balance(bal), nr_hands(0) {

	}

	double get_balance() const {
		return balance;
	}

	int get_hands_played() const {
		return nr_hands;
	}

	void update_balance(double val) {
		balance += val;
		nr_hands++;
	}

	/*
	 * Play this hand
	 *
	 * hand: the current hand to be played
	 * dealer: the dealer's hand
	 */
	virtual void play(Hand * hand, const Hand * dealer) {

		(void)hand;
		(void)dealer;
	}

	// play again?
	virtual bool again() const {

		return false;
	}

	virtual ~Player() {

	}

	static Player * factory(const Config * config);
};

#endif
