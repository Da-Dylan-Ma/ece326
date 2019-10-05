#include "hand.h"
#include "shoe.h"
#include "easybj.h"



Hand *Hand::init(Blackjack* game, char c1, char c2) {
  Hand* hand = new Hand{game};
  hand->addCard(c1);
  hand->addCard(c2);
  return hand;

}

Blackjack *Hand::getGame() const {
  return _game;
}


bool Hand::canSplit() const {
  if (_cards.size() != 2) {
    return false;
  }
  if (_stand) {
    return false;
  }
  if (isT(_cards[0]) && isT(_cards[1])) {
    return true;
  }
  return _cards[0] == _cards[1];

}

Hand* Hand::Split(char c1, char c2) {
  if (!canSplit()) {
    return nullptr;
  }
  _splited = true;
  _history = Blackjack::GameAction::Action_Split;
  Hand* hand = new Hand{_game};
  //remove second card
  char c = _cards.back();
  _cards.pop_back();

  if (c == 'A') {
    _num_ace--;
    _stand = true;
    hand->_stand = true;
  }
  addCard(c1);
  calculate();
  if (_points == 21) {
    _stand = true;
  }

  hand->_splited = true;
  hand->addCard(c);
  hand->addCard(c2);
  if (hand->points() == 21) {
    hand->Stand();
  }
  return hand;
}

Hand::Hand() :
    _game {nullptr}
    , _surrendered{false}
    , _splited {false}
    , _stand {false}
    , _doubled{false}
    ,_soft{false}
    ,_bets{1.0}
    ,_points{0}
    ,_num_ace{0}
    ,_cards{}
    ,_history{Blackjack::GameAction::Action_Null }{
  _cards.reserve(10);
};

Hand::Hand(Blackjack* game):
    Hand() {
  _game = game;
};

void Hand::addCard(char c) {
  if (isalpha(c)) {
    c = (char)toupper(c);
  }
  if (c == 'A') {
    _num_ace++;
  }
  _cards.emplace_back(c);
  calculate();
}


void Hand::setSurrender() {
  _surrendered = true;
  _history = Blackjack::GameAction::Action_Surrender;
}

bool Hand::isInitialHand() const {
  return _cards.size() == 2;
}

void Hand::Hit(char c) {
  if (isAlive()) {
    addCard(c);
    _history = Blackjack::GameAction::Action_Hit;
    if (_points == 21) {
      _stand = true;
    }
  }
}


bool Hand::isStand() const {
  return _stand;
}

void Hand::Stand() {
  if (isAlive()) {
    _stand = true;
    _history = Blackjack::GameAction::Action_Stand;
  }
}


bool Hand::isSplit() const {
  return _splited;
}

void Hand::Double(char c) {
  _doubled = true;
  _stand = true;
  addCard(c);
  _bets *= 2;
  _history = Blackjack::GameAction::Action_Double;
}

bool Hand::isBust() const {
  return _points > 21;
}

bool Hand::isAlive() const {
  return (!isBust()) && (!_surrendered);
}

bool Hand::isBlackJack() const {
  if (!_splited) {
    return _points == 21 && isInitialHand();
  }
  return false;
}

void Hand::calculate() {
  _points = 0;
  for (const char& card : _cards) {
    if (isT(card)) {
      _points += 10;
    } else if (card >= '2' && card <= '9') {
      _points += (card - '0');
    }
  }
  if (_num_ace > 0) {
    int max;
    for (max = _num_ace; max; max--) {
      if (max * 11 + _points <= 21) {
        _points += max * 11;
        _soft = true;
        break;
      } else {
        _points += 1;
      }
    }
    if (max == 0) {
      _soft = false;
    }
  }
}

std::ostream &operator<<(std::ostream &os, const Hand *hand) {
  for (const char& c : hand->_cards) {
    os << c << " ";
  }
  os << "(";
  if (hand->isBlackJack()) {
    os << "blackjack)";
    return os;
  }
  if (hand->isBust()) {
    os << "bust)";
  } else {
    if (hand->isSoft()) {
      os << "soft ";
    }
    os << hand->points() << ")";
  }

  if (hand->_surrendered) {
    os << " SURRENDER";
  } else if (hand->isDouble()) {
    os << " DOUBLE";
  }
  return os;
}
