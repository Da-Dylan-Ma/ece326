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
    Shoe* shoe; // to allow hit
    std::vector<char> cards;
    bool action_allowed;
    bool action_taken = false;
    bool doubled = false;
    bool can_player_split = true;
    char split_card = 0; // card if Hand pending split, 0 otherwise
    bool surrendered = false;

public:
    Hand(Shoe*, char);

    /*----- QUERIES -----*/
    bool is_blackjack() const;
    bool is_bust() const;
    bool has_ace() const;
    bool can_play() const;
    bool can_double() const;
    bool has_doubled() const;
    bool can_surrender() const;
    bool has_surrendered() const;
    bool can_split() const;

	friend std::ostream& operator<<(std::ostream&, const Hand&);

    /*----- GETTERS -----*/
    char get_split_card() const;
    int get_num_cards() const;
    int get_hand_value() const;
    int get_hand_value_min() const;

    /*----- SETTERS -----*/
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
    std::vector<Hand*> hands;
    Hand* dhand; // dealer's hand
    bool blackjack_found = false; // determine if game should continue
    double profit = 0.0; // earnings in single game

    const double INITIAL_BET = 1.0;
    const unsigned int MAX_HAND_NUM = 4;

public:
	Blackjack(Player * p, Shoe * s);
	~Blackjack();

	Hand* start();
	const Hand* dealer_hand() const;
	Hand* next();
	void finish();
    void payout(double);
    void print_encounter(Hand*);

	friend std::ostream& operator<<(std::ostream&, const Blackjack&);
};

std::string to_currency(double v); // Returns str repr of currency for v

#endif
