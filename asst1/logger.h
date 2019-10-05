#ifndef LOGGER_H
#define LOGGER_H
/*
 * a simple logger used for debug reason
 * found it will affect performance dramatically
 * but it is really useful when debugging
 * but it can also be used for other projects
 */
#include <iostream>
#include <string>
#include <sstream>


//set it true when debug, false when release
//you can also use conditional compile

//const bool LoggerActive = true;
class Logger {
public:
  explicit Logger(std::ostream& os, bool active) :
    _print_tag {true}
  , _active {active}
  , _os {os}
  , _tag {"DebugMsg:"} {};
  virtual ~Logger() = default;

public:
  void setActive(bool active) {_active = active; }
  Logger& tag(const std::string& tag) {
    _tag = tag;
    return *this;
  }
  Logger& log(const std::string& tag, const std::string& msg) {
    if (!_active) return *this;
    if (_print_tag) {
      _os << tag <<": ";
    }

    _os << msg;
    _print_tag = false;
    return *this;
  }
  /*
   * overload << so it looks like a output stream
   * but it has other function
   */
  Logger& operator<<(const std::string& str) {
    return log(_tag, str);
  }
  Logger& operator<<(const int value) {
    return log(_tag, std::to_string(value));
  }
  Logger& operator<<(const double value) {
    return log(_tag, std::to_string(value));
  }
  Logger& operator<<(std::basic_ostream<char>& (*os)(std::basic_ostream<char>&)) {
    if (_active) {
      _os << os;
      _print_tag = true;
    }

    return *this;
  }
  //specialization template functions
  template <typename T>
  friend Logger& operator<<(Logger& logger, const T& value) {
    std::stringstream ss{};
    ss << value;
    logger << ss.str();
    return logger;
  }

  //specialization template functions for pointer
  template <typename T>
  friend Logger& operator<<(Logger& logger, T* value) {
    std::stringstream ss{};
    ss << value;
    logger << ss.str();
    return logger;
  }
private:
  bool _print_tag;
  bool _active;
  std::ostream& _os;
  std::string _tag{"DebugMsg:"};
};

/*
 * some static logger, you can also define other
 * logger, for example it can output to a log file
 * however in this project i must comment it out because of -Werror option
 */
//static Logger logger{std::cout, LoggerActive};
//static Logger err{std::cerr, LoggerActive};
#endif
