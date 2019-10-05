/*
 * player.cpp
 *
 * Note: firstly i choose to use a more flexible
 * strategy look up table approach, however when doing profiling i found
 * that searching in map consumes most of the time
 * so i eventually switch to a hard coded strategy look up table
 * hope it will help
 *
 * University of Toronto
 * Fall 2019
 */

#include "player.h"
#include "config.h"
#include "easybj.h"
#include "hand.h"
#include "utils.h"
#include <cassert>
#include <map>
#include <cstring>
#include <sstream>
#include <fstream>

/*
 * base class of automatic and manual player
 * because some code are shared
 * in both of player classes, i think it would be
 * better to put them in a base class
 */
class MyPlayer: public Player {
public:
  explicit MyPlayer(const Config* config) : Player(),  _config{config} {}
  virtual ~MyPlayer() override = default;

public:

  /*
   * a method must be overrided by derivatives
   * select an action from actions set
   * actions set is offered by game based on current game situation
   * e.g. current possible actions.
   */
  virtual Blackjack::GameAction  selectAction(const Hand *hand, const Hand *dealer_hand,
                                              const std::set<Blackjack::GameAction> &ops) = 0;
  virtual void printCurrentDraw(const Hand *hand, const Hand *dealer_hand) = 0;
  void play(Hand *hand, const Hand *dealer) override {

    if (!hand || !dealer) {
      return;
    }
    //silent mode is detected here
    //it seems not a good idea but all possible
    //errors have been found at argument parsing stage
    //so if we come here, it should have no problems
    printCurrentDraw(hand, dealer);
    Blackjack* game = hand->getGame();
    if (game) {
      std::set<Blackjack::GameAction > ops{};
      game->PossiblePlayerActions(hand, ops);
      if (!ops.empty()) {
        Blackjack::GameAction op = selectAction(hand, dealer, ops);
        if (op != Blackjack::GameAction::Action_Null) {
          game->doAction(Blackjack::GameRole::Role_Player, hand, op);
        }
      }
    }
  }

protected:
  const Config* _config;
};

class ManualPlayer : public MyPlayer {
public:
  explicit ManualPlayer(const Config* config) :
      MyPlayer(config) {

  }
  ~ManualPlayer() override = default;
public:

  void printCurrentDraw(const Hand *hand, const Hand *dealer) override {
    std::cout << "Dealer: " << dealer << std::endl;
    std::cout << "Player: " << hand << std::endl;
  }

  bool again() const override {
    std::cout << "Press Any Key to Continue, (Q to Quit):" << std::endl;
    char input = (char)read_input();
    if (input) {
      if (isalpha(input)) {
        input = (char)toupper(input);
        if (input == 'Q') {
          return false;
        }
      }
      return true;
    }
    return true;
  }

  /*
   * select action from options
   * asking user for input
   * will block util user input a valid option
   */
  // menu like: Stand (S) Hit (H) Double (D) Split (P) Surrender (R):
  Blackjack::GameAction selectAction(const Hand *hand, const Hand *dealer, const std::set<Blackjack::GameAction> &ops) override {
    (void)hand;
    (void)dealer;
    while (1) {
      size_t count = 0;
      char input = 0;
      if (ops.find(Blackjack::GameAction::Action_Stand) != ops.end()) {
        std::cout << "Stand (S)";
        count++;
      }
      if (ops.find(Blackjack::GameAction::Action_Hit) != ops.end()) {
        if (count != 0) {
          std::cout << " ";
        }
        std::cout << "Hit (H)";
        count++;
      }
      if (ops.find(Blackjack::GameAction::Action_Double) != ops.end()) {
        if (count != 0) {
          std::cout << " ";
        }
        std::cout << "Double (D)";
        count++;
      }
      if (ops.find(Blackjack::GameAction::Action_Split) != ops.end()) {
        if (count != 0) {
          std::cout << " ";
        }
        std::cout << "Split (P)";
        count++;
      }
      if (ops.find(Blackjack::GameAction::Action_Surrender) != ops.end()) {
        if (count != 0) {
          std::cout << " ";
        }
        std::cout << "Surrender (R)";
      }
      std::cout << ":";
      input = read_input();
      Blackjack::GameAction player_op = Blackjack::toOperation(input);
      if (player_op != Blackjack::GameAction::Action_Null && ops.find(player_op) != ops.end()) {
        return player_op;
      }
    }
  }

};


class AutoPlayer : public MyPlayer {
public:
  //define a strategy look up table key type
  using StrategyLutCoordinate = std::pair<std::string, std::string>;

public:
  explicit AutoPlayer(const Config* config) :
      MyPlayer(config)
      ,_strategies{}  {

  }
  ~AutoPlayer() override = default;
public:
  void printCurrentDraw(const Hand *hand, const Hand *dealer_hand) override {
    (void)hand;
    (void)dealer_hand;
  }

  /*
   * select action based on  strategy map
   */
  Blackjack::GameAction selectAction(const Hand *hand, const Hand *dealer, const std::set<Blackjack::GameAction> &actions) override {
    //find pattern of dealer
    int row = rowNum(hand);
    int alt_row = alternativeRow(hand);
    int col = colNum(dealer);

    Blackjack::GameAction action = Blackjack::GameAction::Action_Null;
    if (_strategies[col][row][0] != 0) {
      //find a action based on strategy string
      action = selectionActionByStrategy(_strategies[col][row], actions);
      //if it is an invalid action
      if (action == Blackjack::GameAction::Action_Null && alt_row != row) {
        //find alternative action by its alternative pattern
        if (_strategies[col][alt_row][0] != 0) {
          action = selectionActionByStrategy(_strategies[col][alt_row], actions);
        }
      }
    }
    return action;
  }

  bool again() const override {
    return get_hands_played() < _config->num_hands;
  }

public:
  /*
   * factory method used here
   * because the return value could possibly be nullptr
   */
  static AutoPlayer* factory(const Config *config) {
    AutoPlayer* ret = new AutoPlayer(config);
    assert(ret);
    if (ret->parseStrategyFile(config->strategy_file)) {
      return ret;
    }
    delete(ret);
    return nullptr;

  }


private:
  /*
   * parsing input file and
   * build strategy look up table
   * return false if error detected
   */
  bool parseStrategyFile(const char* file){
    memset(_strategies, 0, 4 * 23 * 35);
    if (!file) {
      return false;
    }
    std::ifstream ifs{file};
    if (ifs) {
      char line_buf[MAXLINE + 1] = {0};
      for (int line = 0; line < 36 && ifs.getline(line_buf, MAXLINE); line++) {
        if (line) {
          std::stringstream ss{line_buf};
          std::string str{};
          for (int col = 0; col < 24 && ss >> str; col++) {
            if (col && str.size() > 0 && str.size() <= 3) {
              size_t i = 0;
              for (i = 0; i < str.size(); i++) {
                _strategies[col - 1][line - 1][i] = str[i];
              }
              _strategies[col - 1][line - 1][i] = 0;
            }
          }
        }
      }
      ifs.close();
      return true;
    }
    return false;
  }

  /*
   * return an action based on strategy string like "Dh"
   * the result must be included in both strategy string and action set
   * otherwise it will return Action_Null
   */
  static Blackjack::GameAction selectionActionByStrategy(const char* strategy_str, const std::set<Blackjack::GameAction> &actions) {
    for (int i = 0; i < 4 && strategy_str[i] != 0; i++) {
      if (isalpha(strategy_str[i])) {
        char uc = (char)toupper(strategy_str[i]);
        switch (uc) {
          case 'H':
            return Blackjack::GameAction::Action_Hit;
          case 'S':
            return Blackjack::GameAction::Action_Stand;
          case 'D':
            if (actions.find(Blackjack::GameAction::Action_Double) != actions.end()) {
              return Blackjack::GameAction::Action_Double;
            }
            break;
          case 'P':
            if (actions.find(Blackjack::GameAction::Action_Split) != actions.end()) {
              return Blackjack::GameAction::Action_Split;
            }
            break;
          case 'R':
            if (actions.find(Blackjack::GameAction::Action_Surrender) != actions.end()) {
              return Blackjack::GameAction::Action_Surrender;
            }
            break;
          default:
            break;
        }
      }

    }
    return Blackjack::Action_Null;
  }

  /*
   * find row of look up table
   */
  static int rowNum(const Hand *hand) {
    //logger.tag("Row num") << "For hand " <<hand << "  row num is ";
    if (hand->isSoft() && hand->canSplit()) {
      //logger << 26 << std::endl;
      return 26; //'AA'
    } else if (hand->isSoft()) {
      int left = hand->points() - 11;
      //logger << 27 + left - 2 << std::endl;
      return 27 + left - 2;
    } else if (hand->canSplit()) {
      if (Hand::isT(hand->_cards[0])) {
        //logger << 25 << std::endl;
        return 25; //"TT"
      }
      //logger << 17 + (hand->_cards[0] - '2') << std::endl;
      return 17 + (hand->_cards[0] - '2');
    } else {
      //logger << hand->points() - 4 << std::endl;
      return hand->points() - 4;
    }
  }

  static int alternativeRow(const Hand* hand) {
    //logger.tag("Alternative row") << hand->points() - 4 << std::endl;
    return hand->points() - 4;
  }

  /*
   * similar to convertPlayerPattern
   * but number of possible dealer's patterns is
   * less then that of player's
   */
  static int colNum(const Hand* hand) {
    //logger.tag("Col num") << "For hand " << hand << " col num is ";
    if (hand->isSoft() && hand->points() <= 17) {
      int left = hand->points() - 11;
      //logger << 17 + left - 1 << std::endl;
      return 17 + left - 1;
    }
    //logger << hand->points() - 4 << std::endl;
    return hand->points() - 4;
  }
private:
  //strategy lut, find strategy based on player's and dealer's pattern
  char  _strategies[23][35][4];
};




Player * Player::factory(const Config * config)
{
  if (!config->strategy_file) {
    return new ManualPlayer(config);
  } else {
    return AutoPlayer::factory(config);
  }
}

