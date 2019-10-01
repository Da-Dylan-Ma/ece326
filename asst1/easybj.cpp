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



/****************************
**    UTILITY FUNCTIONS    **
****************************/

int card_value(char card) {
    switch (card) {
        case 'A': return 1;
        case 'T':
        case 'J':
        case 'Q':
        case 'K': return 10;
        default: return std::stoi(&card, nullptr, 10);
    }
    return -1; // error
}



/***********************
**    HAND METHODS    **
***********************/

Hand::Hand(Shoe* s, char card_from_split=0): shoe(s) {
    if (card_from_split == 0) {
        action_allowed = true;
        this->add_card(shoe->pop());
        this->add_card(shoe->pop());
    } else {
        action_allowed = card_from_split != 'A'; // disable action after "AA" split
        this->add_card(card_from_split);
        this->add_card(shoe->pop());
    }
}

bool Hand::is_blackjack() const {
	if (this->get_num_cards() != 2) return false;
    if (this->action_taken) return false;
	return this->get_hand_value() == 21;
}
bool Hand::is_bust() const { return this->get_hand_value_min() > 21; }
bool Hand::has_ace() const {
	for (char card: this->cards)
		if (card == 'A') return true;
	return false;
}

// Check possible actions for printing and user input
bool Hand::can_play() const {
    if (!this->action_allowed) return false;
    return this->get_hand_value() < 21; // autostand at 21
}
bool Hand::can_double() const { return this->get_num_cards() == 2; }
bool Hand::has_doubled() const { return this->doubled; }
bool Hand::can_surrender() const { return !this->action_taken; }
bool Hand::has_surrendered() const { return this->surrendered; }
bool Hand::can_split() const {
	if (!this->can_player_split) return false;
	if (this->get_num_cards() != 2) return false;
	return card_value(cards[0]) == card_value(cards[1]);
}

// Print Hand description
std::ostream& operator<<(std::ostream& ostr, const Hand& hand) {
	for (char card: hand.cards) ostr << card << " "; // print cards
	int hand_value = hand.get_hand_value();
    int hand_value_min = hand.get_hand_value_min();
    if (hand_value == 21) {
        ostr << (hand_value_min == 21? "(hard 21)" : (hand.is_blackjack()? "(BJ)" : "(soft 21)"));
    } else if (hand_value > 21) {
        ostr << "(bust)";
    } else {
        ostr << "(" << hand_value << ")";
    }
    // Print "DOUBLE" text only when game has ended
    if (!hand.action_allowed && hand.has_doubled()) ostr << " DOUBLE";
    return ostr;
}

// Returns card if hand needs to be split, otherwise 0
char Hand::get_split_card() const { return this->split_card; }
int Hand::get_num_cards() const { return this->cards.size(); }

// Get highest possible value of hand
int Hand::get_hand_value() const {
	int value = this->get_hand_value_min();
	if ((value <= 11) && (this->has_ace())) return value + 10;
	return value;
}

// Get lowest possible value of hand, i.e. 'A' == 1
int Hand::get_hand_value_min() const {
    int value = 0;
    for (char card: this->cards) value += card_value(card);
    return value;
}

// Get player/dealer Hand code
std::string Hand::get_code(bool is_dealer=false) const {
    int value = 0;
    for (char card: cards) value += card_value(card);
    if (cards.size() == 2) {
        if (cards[0] == cards[1]) {
            if (cards[0] == 'A') return "AA"; // special AA
            if (!is_dealer) {
                if (card_value(cards[0]) == 10) return "TT";
                return std::string(2, cards[0]); // split
            }
        }
    }
    if (value >= 11) return std::to_string(value); // hard
    if (this->has_ace()) {
        if (!is_dealer || value<=7) return "A"+std::to_string(value-1); // soft
        return std::to_string(value+10); // dealer cannot hit > A6
    }
    return std::to_string(value); // hard
}

void Hand::add_card(char card) { this->cards.push_back(card); }
void Hand::call_stand() {
    this->action_taken = true;
    this->action_allowed = false;
}
void Hand::call_hit() {
    this->add_card(shoe->pop());
    this->action_taken = true;
    this->action_allowed = this->get_hand_value_min() < 21; // autostand at 21
}
void Hand::call_double() {
    this->doubled = true;
    this->call_hit();
}
void Hand::disable_split() { this->can_player_split = false; }
void Hand::call_split() { this->split_card = cards[0]; }
void Hand::call_surrender() {
    surrendered = true;
    this->call_stand();
}



/****************************
**    BLACKJACK METHODS    **
****************************/

Blackjack::Blackjack(Player * p, Shoe * s): player(p), shoe(s) {
    dhand = new Hand(shoe);
    Hand* hand = new Hand(shoe);
    if (dhand->is_blackjack() || hand->is_blackjack())
        blackjack_found = true;
    hands.push_back(hand);
}
Blackjack::~Blackjack() {
    delete dhand;
    for (Hand* hand: hands) delete hand;
}

// Return hand for dealer, or nullptr if game ended
const Hand* Blackjack::dealer_hand() const {
    return blackjack_found? nullptr : dhand;
}

// Returns the initial player hand, and start the game. nullptr if game ended
Hand* Blackjack::start() {
    if (blackjack_found) return nullptr;
    return hands[0];
}

// Returns the next hand the player can play, nullptr otherwise
Hand* Blackjack::next() {
    // Process hand splitting first
    for (unsigned int i = 0; i < hands.size(); i++) {
        char split_card = hands[i]->get_split_card();
        if (split_card != 0) {
            Hand* new_hand_1 = new Hand(shoe, split_card);
            Hand* new_hand_2 = new Hand(shoe, split_card);
            hands.erase(hands.begin()+i); // insert at same position
            hands.insert(hands.begin()+i, new_hand_2);
            hands.insert(hands.begin()+i, new_hand_1);
        }
    }
    // Disable splitting if exceeded number of allowed hands
    if (hands.size() == MAX_HAND_NUM)
        for (Hand* hand: hands) hand->disable_split();

    // Select next hand
    for (Hand* hand: hands) {
        if (hand->can_play()) {
            return hand;
        }
    }
    return nullptr; // end player turn
}

// Calculate profit earned by player and update `player->balance`
// Called once next() returns nullptr
void Blackjack::finish() {

    // Check if blackjack condition
    if (blackjack_found) {
        Hand* hand = hands[0];
        if (hand->is_blackjack()) {
            payout(INITIAL_BET * 1.5);
        } else if (dhand->is_blackjack()) {
            payout(INITIAL_BET * -1);
        } else {
            payout(0);
        }
        return;
    }

    // Check if player surrendered
    Hand* hand = hands[0];
    if (hand->has_surrendered()) {
        payout(INITIAL_BET * -0.5);
        return;
    }

    // Dealer's turn to draw
    // Dealer will not draw if player has busted all hands
    bool player_busted = true;
    for (Hand* hand: hands) {
        if (!hand->is_bust()) player_busted = false;
    }
    if (!player_busted) {
        while (true) {
            if (dhand->get_hand_value_min() == 7 && dhand->has_ace()) {
                dhand->call_hit();
                continue;
            }
            if (dhand->get_hand_value() < 17) {
                dhand->call_hit();
            } else {
                dhand->call_stand();
                break;
            }
        }
    }

    // Dealer busted, all live hands win
    if (dhand->is_bust()) {
        for (Hand* hand: hands) {
            int bet = INITIAL_BET * (hand->has_doubled()? 2 : 1);
            payout(hand->is_bust()? 0 : bet);
        }
        return;
    }

    // Dealer not busted, compare
    int dealer_value = dhand->get_hand_value();
    for (Hand* hand: hands) {
        int bet = INITIAL_BET * (hand->has_doubled()? 2 : 1);
        int hand_value = hand->get_hand_value();
        if (hand_value < dealer_value || hand->is_bust()) {
            payout(bet * -1);
        } else if (hand_value > dealer_value) {
            payout(bet);
        } else {
            payout(0);
        }
    }
}

void Blackjack::payout(double amount) {
    player->update_balance(amount);
    profit += amount;
}

// Print results of one round
std::ostream& operator<<(std::ostream& ostr, const Blackjack& bj) {
    ostr << "Dealer: " << *(bj.dhand) << std::endl;
    for (unsigned int i = 0; i < bj.hands.size(); i++) {
        Hand* hand = bj.hands[i];
        ostr << "Hand " << i+1 <<": " << *hand << std::endl;
    }
    ostr << "Result: " << to_currency(bj.profit) << std::endl;
    ostr << "Current Balance: " << to_currency(bj.player->get_balance()) << std::endl;
    ostr << std::flush;
	return ostr;
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
