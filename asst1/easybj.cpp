/*
 * easybj.cpp
 *
 * Note: change this file to implement Blackjack logic
 *
 * University of Toronto
 * Fall 2019
 */

#include "easybj.h"
#include "player.h"
#include "shoe.h"
#include <sstream>
#include <iomanip>
#include <iostream>

// Converts card to value, 'A' == 1
int card_value(char card) {
    switch (card) {
        case 'A':
            return 1;
        case 'T':
        case 'J':
        case 'Q':
        case 'K':
            return 10;
        default:
            return std::stoi(&card, nullptr, 10);
    }
    return -1; // error
}

Hand::Hand(Player* p, Shoe* s):
	player(p), shoe(s), bet(1.0),
	action_taken(false), action_allowed(true),
	split_card(0), can_player_split(true) {}

Hand::Hand(Player* p, Shoe* s, char card_from_split):
	player(p), shoe(s), bet(1.0),
	action_taken(true), action_allowed(card_from_split != 'A'),
	split_card(0), can_player_split(true) {}

// Checks if hand is blackjack
bool Hand::is_blackjack() const {
	if (this->get_num_cards() != 2) return false;
    if (this->action_taken) return false;
	return this->get_hand_value() == 21;
}

// Checks if hand is busted
bool Hand::is_bust() const { return this->get_hand_value_min() > 21; }

// Check if hand contains ace
bool Hand::has_ace() const {
	for (char card: this->cards) {
		if (card == 'A') return true;
	}
	return false;
}

// Check possible actions for printing and user input
bool Hand::can_play() const {
    if (!this->action_allowed) return false;
    return this->get_hand_value() < 21;
}

// Check if can double, i.e. two card hand
bool Hand::can_double() const { return this->get_num_cards() == 2; }

// Check if action taken
bool Hand::can_surrender() const { return !this->action_taken; }

// Check if can split, i.e. same value in two card hand
bool Hand::can_split() const {
	if (!this->can_player_split) return false;
	if (this->get_num_cards() != 2) return false;
	return card_value(cards[0]) == card_value(cards[1]);
}

// Print Hand
std::ostream& operator<<(std::ostream& ostr, const Hand& hand) {
	// Print hand cards
	for (char card: hand.cards) ostr << card << " ";

	// Print value
	int hand_value = hand.get_hand_value();
    int hand_value_min = hand.get_hand_value_min();
    if (hand_value == 21) {
        if (hand_value_min == 21) {
            ostr << "(hard 21)";
        } else {
            ostr << (hand.is_blackjack() ? "(BJ)" : "(soft 21)");
        }
    } else if (hand_value > 21) {
        ostr << "(bust)";
    } else {
        ostr << "(" << hand_value << ")";
    }

    // Print double
    if (!hand.action_allowed && (hand.bet == 1.0*2)) ostr << " DOUBLE";
    return ostr;
}

// Returns card if hand needs to be split, otherwise 0
char Hand::get_split_card() const { return this->split_card; }

// Get number of cards in hand, for double and split, i.e. cards.length
int Hand::get_num_cards() const { return this->cards.size(); }

// Get highest possible value of hand (under 21 if possible)
int Hand::get_hand_value() const {
	int value = this->get_hand_value_min();
	if ((value <= 11) && (this->has_ace())) {
		return value + 10;
	}
	return value;
}

// Get lowest possible value of hand, i.e. 'A' == 1
int Hand::get_hand_value_min() const {
    int value = 0;
    for (char card: this->cards) {
        value += card_value(card);
    }
    return value;
}

// Update hand, stand and surrender does nothing to Hand itself
// Add card to hand, using Shoe reference
void Hand::add_card() {
    this->cards.push_back(this->shoe->pop());
}
void Hand::add_card(char card) {
    // Called only when split
    this->cards.push_back(card);
    this->action_taken = true;
}

// Disable splitting, called in Blackjack
void Hand::disable_split() { this->can_player_split = false; }

// Stand
void Hand::call_stand() {
    this->action_taken = true;
    this->action_allowed = false;
}

// Perform hit procedure
void Hand::call_hit() {
    this->add_card();
    this->action_taken = true;
    this->action_allowed = this->get_hand_value_min() < 21; // automatic stand at 21
}

// Perform doubling procedure
void Hand::call_double() { this->bet *= 2; this->call_hit(); }

// Returns new Hand with cards split
void Hand::call_split() {
    this->split_card = cards[0];
    // Rest of action performed in Blackjack
    // action_allowed = cards[0] != 'A'
    // Hand* other = new Hand(p, s, action_allowed);
    // this.add_card(); // which order?
    // other.add_card();
    // return other;
}

// Surrender
void Hand::call_surrender() {
    this->call_stand();
    surrendered = true;
}

Blackjack::Blackjack(Player * p, Shoe * s):
    player(p), shoe(s), blackjack_found(false), profit(0.0) {

    dealer_hand_ptr = new Hand(p, s);
    dealer_hand_ptr->add_card();
    dealer_hand_ptr->add_card();
    if (dealer_hand_ptr->is_blackjack()) blackjack_found = true;

    Hand* player_hand = new Hand(p, s);
    player_hand->add_card();
    player_hand->add_card();
    if (player_hand->is_blackjack()) blackjack_found = true;

    hands.push_back(player_hand);
}

Blackjack::~Blackjack() {
    delete dealer_hand_ptr;
    for (Hand* hand: hands) delete hand;
}

// Return hand for dealer, or nullptr if game ended
const Hand* Blackjack::dealer_hand() const {
    if (blackjack_found) return nullptr;
    return dealer_hand_ptr;
}

// Returns the initial player hand, and start the game (?)
Hand * Blackjack::start() {
    if (blackjack_found) return nullptr;
    this->print_encounter(hands[0]);
    return hands[0];
}

// Returns the next hand the player can play
// Returns nullptr once the player subroutine ends
// This function may only be called after start(), and returns the next hand that the player can play. The return value may be nullptr if no more hands are left to be played. Note that if a hand has 21 points, it stands automatically.
Hand * Blackjack::next() {

    // Process hand splitting first
    for (unsigned int i = 0; i < hands.size(); i++) {
        char split_card = hands[i]->get_split_card();
        if (split_card != 0) {
            Hand* new_hand_1 = new Hand(this->player, this->shoe, split_card);
            Hand* new_hand_2 = new Hand(this->player, this->shoe, split_card);
            new_hand_1->add_card(split_card);
            new_hand_1->add_card();
            new_hand_2->add_card(split_card);
            new_hand_2->add_card();

            hands.erase(hands.begin()+i); // insert at same position
            hands.insert(hands.begin()+i, new_hand_2);
            hands.insert(hands.begin()+i, new_hand_1);
        }
    }

    // Disable splitting if exceeded
    if (hands.size() == 4)
        for (Hand* hand: hands) hand->disable_split();

    for (Hand* hand: hands) {
        if (hand->can_play()) {
            this->print_encounter(hand);
            return hand;
        }
    }
    return nullptr;
}

// For string representation printing, not critical
// Do we need to print (blackjack) for blackjack case?
std::ostream & operator<<(std::ostream & ostr, const Blackjack & bj) {
    // Dealer results
    ostr << "Dealer: " << *(bj.dealer_hand_ptr) << std::endl;

    // Player results
    int hand_num = 1;
    for (Hand* hand: bj.hands) {
        ostr << "Hand " << hand_num++ <<": " << *hand << std::endl;
    }
    ostr << "Result: " << to_currency(bj.profit) << std::endl;
    ostr << "Current Balance: " << to_currency(bj.player->get_balance()) << std::endl;
    // double result = bj.profit;
    // double bal = bj.player->get_balance();
    // std::string dollar_sign;
    // if (bal < 0.0) {
    //     dollar_sign = "-$";
    //     bal = -bal;
    //     result = -result;
    // } else {
    //     dollar_sign = "$";
    // }
    // ostr << "Result: " << dollar_sign;
    // ostr << std::fixed << std::setprecision(2) << result << std::endl;
    // ostr << "Current Balance: " << dollar_sign;
    // ostr << std::fixed << std::setprecision(2) << bal << std::endl;
	return ostr;
}

// Calculate profit earned by player and update `player->balance`
// This function may only be called after no more hands are left to be played. Its purpose is to allow the dealer to take action(s) and then updates the player's balance based on the outcome of the game. If the player has no live hands (i.e. all his/her hands busted or surrendered), then the dealer will not draw any cards. In all circumstances, you MUST call Player::update_balance exactly once during this function otherwise the number of hands played will be off.
void Blackjack::finish() {

    // Blackjack payoff
    if (blackjack_found) {
        Hand* player_hand = hands[0];
        if (player_hand->is_blackjack()) {
            player->update_balance(player_hand->bet * 1.5);
            profit += player_hand->bet * 1.5;
        } else if (dealer_hand_ptr->is_blackjack()) {
            player->update_balance(player_hand->bet * -1);
            profit += player_hand->bet * -1;
        } else {
            player->update_balance(0.0);
        }
        return;
    }

    // No blackjack payoff
    // Check if player surrendered
    Hand* player_hand = hands[0];
    if (player_hand->surrendered) {
        player->update_balance(player_hand->bet * -0.5);
        profit += player_hand->bet * -0.5;
        return;
    }

    // Check if player is all bust, dealer will not draw cards in this case
    bool player_bust = true;
    for (Hand* hand: hands) {
        if (!hand->is_bust()) {
            player_bust = false;
            break;
        }
    }
    if (!player_bust) {
        // Dealer actions
        while (true) {
            int dealer_value = dealer_hand_ptr->get_hand_value_min();
            if (dealer_value == 7 && dealer_hand_ptr->has_ace()) {
                dealer_hand_ptr->call_hit();
                continue;
            }
            dealer_value = dealer_hand_ptr->get_hand_value();
            if (dealer_value < 17) {
                dealer_hand_ptr->call_hit();
            } else {
                dealer_hand_ptr->call_stand();
                break;
            }
        }
    }

    // Calculate profit
    if (dealer_hand_ptr->is_bust()) {
        for (Hand* hand: hands) {
            if (hand->is_bust()) {
                player->update_balance(0.0);
            } else {
                player->update_balance(hand->bet);
                profit += hand->bet;
            }
        }
    } else {
        int dealer_value = dealer_hand_ptr->get_hand_value();
        for (Hand* hand: hands) {
            int hand_value = hand->get_hand_value();
            if (hand_value < dealer_value || hand->is_bust()) {
                player->update_balance(hand->bet * -1);
                profit += hand->bet * -1;
            } else if (hand_value > dealer_value) {
                player->update_balance(hand->bet);
                profit += hand->bet;
            } else {
                player->update_balance(0.0);
            }
        }
    }
}

void Blackjack::print_encounter(Hand* hand) {
    std::cout << "Dealer: " << *dealer_hand_ptr << std::endl;
    std::cout << "Player: " << *hand << std::endl;
}

std::string to_currency(double v) {
	std::ostringstream ostr;

	ostr << std::fixed << std::setprecision(2);
	if (v > 0) {
		ostr << "+$" << v;
	} else if (v < 0) {
		ostr << "-$" << -v;
	}
	else {
		ostr << "$" << v;
	}

	return ostr.str();
}
