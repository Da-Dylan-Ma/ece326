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

Blackjack::Blackjack(Player * p, Shoe * s)
	: player(p)
	, shoe(s)
{
	/*
	 * TODO: implement this
	 */
}

Blackjack::~Blackjack()
{
	/*
	 * TODO: implement this
	 */
}

 
Hand * Blackjack::start() 
{
	/*
	 * TODO: implement this
	 */

	return nullptr;
}

Hand * Blackjack::next() 
{
    /*
	 * TODO: implement this
	 */

	return nullptr;
}

std::ostream & operator<<(std::ostream & ostr, const Blackjack & bj)
{
	/*
	 * TODO: implement this
	 */
	 
	(void)bj;
	return ostr;
}


void Blackjack::finish() 
{
	double profit = 0.;
	
	/*
	 * TODO: implement this
	 */
	
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

