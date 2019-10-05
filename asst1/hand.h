#ifndef HAND_H
#define HAND_H

#include <iostream>
#include <vector>
#include "easybj.h"

class Blackjack;
class Shoe;


class Hand {
public:
  explicit Hand(Blackjack* );
  virtual ~Hand()= default;

  static Hand* init(Blackjack* game, char c1, char c2);

  static bool isT(char c) {
    return c == 'J' || c == 'Q' || c == 'K' || c == 'T';
  }
public:


  Blackjack* getGame() const;

  void Stand();
  void Hit(char c);
  void Double(char c);
  Hand* Split(char c1, char c2);
  Blackjack::GameAction history() const { return  _history; }


  bool isInitialHand() const;
  bool isStand() const;
  bool isSurrendered() const { return _surrendered; };
  bool canSplit() const;
  bool isSplit() const;
  void setSurrender();
  bool isDouble() const { return _doubled; }
  bool isBlackJack() const;
  bool isBust() const;
  bool isAlive() const;
  double bets() const { return _bets; }
  bool isSoft() const { return _soft; }
  int points() const { return _points; }


private:
  Hand();
  void addCard(char c);
  void calculate();
  friend std::ostream&  operator<<(std::ostream& os, const Hand* hand);


public:
  Blackjack* _game;
  bool _surrendered;
  bool _splited;
  bool _stand;
  bool _doubled;
  bool _soft;
  double _bets;
  int _points;
  int _num_ace;
  std::vector<char> _cards;
  Blackjack::GameAction _history;

};

#endif
