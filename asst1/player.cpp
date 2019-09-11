/*
 * player.cpp
 *
 * Note: change this file to implement Player subclass
 *
 * University of Toronto
 * Fall 2019
 */

#include "player.h"

Player * Player::factory(const Config * config)
{
	/*
	 * TODO: implement this
	 */
	 
	(void)config;
	return new Player();
}

