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
#include <set>

 class Player;
class Shoe;
class Config;
class Hand;

class Blackjack {
	Player * player;
	Shoe * shoe;

public:
  enum EndState { PLAYER_BJ, DEALER_BJ, DRAW_BJ, PLAYER_SURRENDER, DEALER_BUST, PLAYER_BUST, ALL_STILL, NOT_END };
  enum GameRole { Role_Dealer, Role_Player };
  enum GameAction { Action_Stand , Action_Hit,  Action_Double, Action_Split, Action_Surrender, Action_Null };
  static GameAction toOperation(char input) {
    if (!isalpha(input)) {
      return Action_Null;
    }
    input = (char)toupper(input);
    switch (input) {
      case 'S':
        return Action_Stand;
      case 'H':
        return Action_Hit;
      case 'D':
        return Action_Double;
      case 'P':
        return Action_Split;
      case 'R':
        return Action_Surrender;
      default:
        return Action_Null;
    }
  }
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
	const Hand * dealer_hand() const { return _dealer_hand; }
	
	/*
	 * Returns next hand to be played (may be the same hand)
	 */
	Hand * next();
	
	/*
	 * Call once next() returns nullptr
	 */
	void finish();

	friend std::ostream & operator<<(std::ostream &, const Blackjack &);

	unsigned long numPlayerHands() const { return  _player_hands.size(); }


	/*
	 *
	 * possible operation
	 */
	 void PossiblePlayerActions(Hand *hand, std::set<GameAction> &actions);

	 /*
	  * do operation
	  */
	 void doAction(GameRole role, Hand* hand, GameAction op);


  //Stand (S) Hit (H) Double (D) Split (P) Surrender (R): p


private:

  /*
   * dealer move
   * with preset strategy
   */
  bool dealerMove();

  /*
   * checkEnd(0) will check end at start function
   * e.g. check black jack
   * checkEnd(1) will check end at next function before dealer move
   * e.g. check surrender, bust, or all stand
   * checkEnd(2) will check end after dealer move
   * no other parameter is available
   */
  EndState checkEnd(int what_stage) const;

  void setEndState(EndState state) {_state = state;}

private:
  /*
   *
   */
	void PlayerSplit(Hand* hand);
	void PlayerStand(Hand* hand);
	void PlayerHit(Hand* hand);
	void PlayerDouble(Hand* hand);
	void PlayerSurrender();

private:
  bool isPlayerAllBust() const;
  Hand* findNextAvailPlayerHand();


private:
	Hand* _dealer_hand;
  EndState _state;
	std::vector<Hand*> _player_hands;
	size_t _cur_hand_index;
  double _profit;

};

/*
 * Returns string representation of currency for v
 */
std::string to_currency(double v);

#endif
