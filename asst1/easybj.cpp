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
#include <sstream>
#include <iomanip>
#include "hand.h"
#include "shoe.h"
#include "logger.h"
#include <cassert>
#include <vector>
#include <set>

Blackjack::Blackjack(Player * p, Shoe * s)
    : player(p)
    , shoe(s)
    , _dealer_hand{nullptr}
    , _state{NOT_END}
    , _player_hands{}
    , _cur_hand_index{0}
    , _profit{0.0} {}

Blackjack::~Blackjack()
{
  if (_dealer_hand) {
    delete(_dealer_hand);
    _dealer_hand = nullptr;
  }
  if (!_player_hands.empty()) {
    for (Hand* hand : _player_hands) {
      delete(hand);
    }
    _player_hands.clear();
  }
}


Hand * Blackjack::start()
{
  std::vector<char> initial_cards(4);
  for (int i = 0; i < 4 ; i++) {
    initial_cards[i] = shoe->pop();
  }
  _dealer_hand = Hand::init(this, initial_cards[0], initial_cards[1]);
  Hand* player_hand = Hand::init(this, initial_cards[2], initial_cards[3]);
  if (_dealer_hand->isBlackJack()) {
    if (player_hand->isBlackJack()) {
      _state = DRAW_BJ;
    } else {
      _state = DEALER_BJ;
    }
  } else if (player_hand->isBlackJack()) {
    _state = PLAYER_BJ;
  }
  _player_hands.push_back(player_hand);
  EndState state = checkEnd(0);
  setEndState(state);
  if (state != NOT_END) {
    return nullptr;
  }
  //add one log so that it will not warning...
  //logger.tag("Start") << "roung start" << std::endl;
  return player_hand;
}

Hand * Blackjack::next()
{

  EndState state = checkEnd(1);
  if (state != NOT_END) {
    setEndState(state);
    return nullptr;
  }


  Hand* ret = findNextAvailPlayerHand();
  if (!ret) {
    while (dealerMove()) {

    }
    state = checkEnd(2);
    if (state != NOT_END) {
      setEndState(state);
      //logger.tag("Next hand") << "gaming end" << std::endl;
      return nullptr;
    }
  }
//  else {
//    //logger.tag("Next Hand") << "game is processing, offering next hand..." << std::endl;
//    //logger.tag("Next Hand") << "current hands are: " << std::endl;
//    for (const Hand* hand : _player_hands) {
//      //logger << hand;
//      if (hand->isStand()) {
//        //logger << " stand";
//      }
//      if (hand == _player_hands[_cur_hand_index]) {
//        //logger << " current";
//      }
//      //logger << std::endl;
//    }
//    return ret;
//  }
  return ret;
}

std::ostream & operator<<(std::ostream & os, const Blackjack & bj)
{
  if (bj._dealer_hand) {
    os << "Dealer: " << bj._dealer_hand << std::endl;
  }
  for (std::vector<Hand*>::size_type i = 0; i < bj._player_hands.size(); i++) {
    os << "Hand " << i + 1 << ": " << bj._player_hands[i] << std::endl;
  }
  os << "Result: " << to_currency(bj._profit) << std::endl;
  os << "Current Balance: " << to_currency(bj.player->get_balance()) << std::endl;
  return os;
}


void Blackjack::finish()
{
  double profit = 0.0;
  //logger.tag("Game Finish") << "game finish ";
  //check game end status
  //then calculate balance.
  switch (_state) {
    case DRAW_BJ:
      //logger << "because of both had black jack" << std::endl;
      profit = 0.0;
      break;
    case PLAYER_BJ: {
     // logger << "because of player had black jack" << std::endl;
      profit = 1.5;
      break;
    }
    case DEALER_BJ:
      //logger << "because of dealer had black jack" << std::endl;
      profit = - 1.0;
      break;
    case PLAYER_SURRENDER: {
      //logger << "because of player surrender" << std::endl;
      profit = -0.5;
      break;
    }
    case DEALER_BUST: {
      //logger << "because of dealer busted" << std::endl;
      profit = 0.0;
      for (const Hand* hand : _player_hands) {
        if (hand->isBust()) {
          profit -= hand->bets();
          continue;
        }
        profit += hand->bets();

      }
      break;
    }
    case PLAYER_BUST: {
      //logger << "because of all player hands bust" << std::endl;
      profit = 0.0;
      for (const Hand* hand : _player_hands) {
        profit -= hand->bets();
      }
      break;
    }
    case ALL_STILL: {
      //logger << "because of no more actions can be done for both sides." << std::endl;
      profit = 0.0;
      for (const Hand* hand: _player_hands) {
        if (hand->isAlive()) {
          if (hand->points() > _dealer_hand->points()) {
            profit += hand->bets();
          } else if (hand->points() < _dealer_hand->points()){
            profit -= hand->bets();
          }
          //draw
        } else {
          profit -= hand->bets();
        }
      }
      break;
    }
    default:
      break;

  }
  _profit = profit;
  player->update_balance(profit);
}

std::string to_currency(double v)
{
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

void Blackjack::PossiblePlayerActions(Hand *hand, std::set<Blackjack::GameAction> &actions) {
  //logger.tag("PossiblePlayerAction");
  //logger << "possible actions are (";
  actions.clear();
  if (hand->isAlive()) {
    if (!hand->isStand()) {
      actions.insert(Action_Hit);
      //logger << "action hit, ";
      actions.insert(GameAction::Action_Stand);
      //logger << "action stand, ";
      if (hand->isInitialHand()) {
        //logger << "action double, ";
        actions.insert(Action_Double);
      }
      if (numPlayerHands() == 1  && hand->isInitialHand()) {
        //logger << "action surrender, ";
        actions.insert(GameAction::Action_Surrender);
      }
      if (hand->canSplit() && _player_hands.size() <= 3) {
        //logger << "action split";
        actions.insert(GameAction::Action_Split);
      }
    }
  }
//  if (actions.empty()) {
//    logger << "no actions now available";
//  }
//  logger << ")" << std::endl;
}

bool Blackjack::dealerMove() {
  //logger.tag("Dealer Move");
  if ( _dealer_hand->isAlive() && !_dealer_hand->isStand()) {
    if (_dealer_hand->points() >= 18) {
      //logger << "Dealer stand because of 18." << std::endl;
      doAction(GameRole::Role_Dealer, _dealer_hand, Action_Stand);
      return false;
    }
    if (_dealer_hand ->points() <= 16) {
      //logger << "Dealer hit because of less than 16." << std::endl;
      doAction(GameRole::Role_Dealer, _dealer_hand, Action_Hit);
    } else if (_dealer_hand->isSoft()) {
      //logger << "Dealer hit on soft 17." << std::endl;
      doAction(GameRole::Role_Dealer, _dealer_hand, Action_Hit);
    } else {
      //logger << "Dealer stand on hard 17." << std::endl;
      doAction(GameRole::Role_Dealer, _dealer_hand, Action_Stand);
    }
    return true;
  }
  return false;
}

void Blackjack::doAction(Blackjack::GameRole role, Hand *hand, Blackjack::GameAction op) {
  if (role == GameRole::Role_Player) {
    //logger.tag("Player Action");
    switch(op) {
      case Action_Stand:
        //logger << "player stand." << std::endl;
        PlayerStand(hand);
        break;
      case Action_Hit:
        //logger << "player hit." << std::endl;
        PlayerHit(hand);
        break;
      case Action_Double:
        //logger << "player double." << std::endl;
        PlayerDouble(hand);
        break;
      case Action_Split:
        //logger << "player split." << std::endl;
        PlayerSplit(hand);
        break;
      case Action_Surrender:
        //logger << "player surrender." << std::endl;
        PlayerSurrender();
        break;
      default:
        break;
    }
  } else {
    //logger.tag("Dealer Action");
    switch(op) {
      case Action_Stand:
        //logger << "dealer stand." << std::endl;
        hand->Stand();
        break;
      case Action_Hit:
        //logger << "dealer hit." << std::endl;
        hand->Hit(shoe->pop());
        break;
      default:
        break;
    }
  }
}

void Blackjack::PlayerStand(Hand *hand) {
  void(this);
  hand->Stand();
}

void Blackjack::PlayerHit(Hand *hand) {
  hand->Hit(shoe->pop());
}

void Blackjack::PlayerDouble(Hand *hand) {
  hand->Double(shoe->pop());

}

void Blackjack::PlayerSurrender() {
  _state = PLAYER_SURRENDER;
  _player_hands[0]->setSurrender();
}

void Blackjack::PlayerSplit(Hand *hand) {
  char c1, c2;
  c1 = shoe->pop();
  c2 = shoe->pop();
  Hand* new_hand = hand->Split(c1, c2);
  assert(new_hand);
  _player_hands.push_back(new_hand);
}

/*
 * check if gaming end
 * if true return the reason that game ends such as player bust
 * or Dealer Bj
 */
Blackjack::EndState Blackjack::checkEnd(int what_stage) const {
  //logger.tag("Checking End");
  if (what_stage == 0) {
    //logger << "checking black jack..." << std::endl;
    if (!_player_hands.empty() && _dealer_hand) {
      if (_player_hands[0]->isBlackJack() && _dealer_hand->isBlackJack()) {
        //logger << "draw blackjack situation." << std::endl;
        return DRAW_BJ;
      } else if (_player_hands[0]->isBlackJack()) {
        //logger << "player blackjack." << std::endl;
        return PLAYER_BJ;
      } else if (_dealer_hand->isBlackJack()) {
        //logger << "dealer blackjack." << std::endl;
        return DEALER_BJ;
      }
      //logger << "neither player or dealer blackjack." << std::endl;
      return NOT_END;
    }
  } else if (what_stage == 1) {
    //logger << "checking player lost situation." << std::endl;
    if (_player_hands[0]->isSurrendered()) {
      //logger << "player surrender." << std::endl;
      return PLAYER_SURRENDER;
    }
    if (isPlayerAllBust()) {
      //logger << "player bust." << std::endl;
      return PLAYER_BUST;
    }
  } else if (what_stage == 2) {
    if (_dealer_hand->isBust()) {
      //logger << "dealer bust." << std::endl;
      return DEALER_BUST;
    }
    if (_dealer_hand->isStand()) {
      //logger << "dealer stand." << std::endl;
      return ALL_STILL;
    }
  }
  //logger << "game is still processing." << std::endl;
  return NOT_END;
}

bool Blackjack::isPlayerAllBust() const {
  //logger.tag("Check Player All bust");
  for (const Hand* hand: _player_hands) {
    if (hand->isAlive()) {
      return false;
    }
  }
  return true;
}

Hand* Blackjack::findNextAvailPlayerHand() {
  //logger.tag("Find Avail") << "finding ..." << std::endl;
  if (_player_hands[_cur_hand_index]->isAlive() && !(_player_hands[_cur_hand_index]->isStand())) {
    if (_player_hands[_cur_hand_index]->history() == Action_Hit || _player_hands[_cur_hand_index]->history() == Action_Split) {
      //logger.tag("Find Avail") << "current hand still processing" << std::endl;
      return _player_hands[_cur_hand_index];
    }
  }
  //logger.tag("Find Avail") << "switching to next available hand." << std::endl;
  size_t start, stop = _cur_hand_index;
  if (_cur_hand_index == _player_hands.size() - 1) {
    start = 0;
  } else {
    start = _cur_hand_index + 1;
  }
//  logger.tag("Find Avail") << "current index is " << _cur_hand_index;
//  logger.tag("Find Avail") << " start is " << start;
//  logger.tag("Find Avail") << " stop is " << stop << std::endl;
  for (_cur_hand_index = start; _cur_hand_index != stop;) {
    if (_player_hands[_cur_hand_index]->isAlive() && !(_player_hands[_cur_hand_index]->isStand())) {
      return _player_hands[_cur_hand_index];
    }
    if (_cur_hand_index < _player_hands.size() - 1) {
      _cur_hand_index++;
    } else {
      _cur_hand_index = 0;
    }
  }
  if (_player_hands[_cur_hand_index]->isAlive() && !(_player_hands[_cur_hand_index]->isStand())) {
    return _player_hands[_cur_hand_index];
  }
  return nullptr;
}



