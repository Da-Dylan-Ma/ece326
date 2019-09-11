 /*
 * easybj.h
 *
 * Header files for Easy Blackjack.
 *
 * Note: change this file to implement Blackjack
 *
 * University of Toronto
 * Fall 2019
 */
 
#ifndef EASYBJ_H
#define EASYBJ_H

#include <string>
#include <iostream>

class Player;
class Shoe;
class Config;
class Hand;

class Blackjack {
	Player * player;
	Shoe * shoe;

public:
	Blackjack(Player * p, Shoe * s);
	~Blackjack();
	
	/*
	 * Start a game of Blackjack
	 *
	 * Returns first hand to be played, nullptr if either dealer or player's
	 * initial hand is blackjack (or both)
	 */
	Hand * start();
	
	/*
	 * Returns dealer's hand
	 */
	const Hand * dealer_hand() const { return nullptr; }
	
	/*
	 * Returns next hand to be played (may be the same hand)
	 */
	Hand * next();
	
	/*
	 * Call once next() returns nullptr
	 */
	void finish();

	friend std::ostream & operator<<(std::ostream &, const Blackjack &);

	// TODO: you may add more functions as appropriate
};

/*
 * Returns string representation of currency for v
 */
std::string to_currency(double v);

#endif
