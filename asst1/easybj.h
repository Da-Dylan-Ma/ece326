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
#include <vector>

class Player;
class Shoe;
class Config;

class Hand {
public:
    Player* player;
    Shoe*shoe;
    std::vector<char> cards;
    double bet;
    bool action_taken;
    bool action_allowed;
    char split_card;
    bool can_player_split;
    bool surrendered = false;
    // int num_splits_left;

    Hand(Player* p, Shoe* s);
    Hand(Player* p, Shoe* s, char card_from_split);

    /*----- QUERIES -----*/
    bool is_blackjack() const;
    bool is_bust() const;
    bool has_ace() const;
    bool can_play() const;
    bool can_double() const;
    bool can_surrender() const;
    bool can_split() const;

    /*----- GETTERS -----*/
    char get_split_card() const;
    int get_num_cards() const;
    int get_hand_value() const;
    int get_hand_value_min() const;

    /*----- SETTERS -----*/
    void add_card();
    void add_card(char card);
    void disable_split();
    void call_stand();
    void call_hit();
    void call_double();
    void call_split();
    void call_surrender();
};

class Blackjack {
	Player * player;
	Shoe * shoe;
    std::vector<Hand*> hands; // Keep track of hands available to be played
    Hand* dealer_hand_ptr; // Save dealer's hand
    bool blackjack_found; // Quick terminate
    double profit; // Total

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
	const Hand * dealer_hand() const; // Returns dealer's hand
	Hand * next(); // Returns next hand to be played (may be the same hand)
	void finish(); // Call once next() returns nullptr
    void print_encounter(Hand* hand);

	friend std::ostream & operator<<(std::ostream &, const Blackjack &);
};

/*
 * Returns string representation of currency for v
 */
std::string to_currency(double v);

#endif
