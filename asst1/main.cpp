/*
 * main.cpp
 *
 * Main function for Easy Blackjack
 *
 * Note: you may not change this file
 *
 * University of Toronto
 * Fall 2019
 */
 
#include "easybj.h"
#include "config.h"
#include "player.h"
#include "shoe.h"
#include <cstdlib>
#include <iostream>
#include <iomanip>

static void player_summary(Player * player);

int 
main(int argc, const char * argv[])
{
	Config config;

	if (config.process_arguments(argc, argv) < 0)
		return EXIT_FAILURE;

	while (!config.shoe->over()) {
		Blackjack game(config.player, config.shoe);
		Hand * hand = game.start();
		const Hand * dealer = game.dealer_hand();
	
		while (hand != nullptr) {
			config.player->play(hand, dealer);
			hand = game.next();
		}
		
		game.finish();	
		if (!config.silent)
			std::cout << game;	
		
		if (!config.player->again())
			break;
	}
	
	player_summary(config.player);
	return EXIT_SUCCESS;
}

static void 
player_summary(Player * player)
{
	int hands_played;
	double balance;
	double advantage;
	
	hands_played = player->get_hands_played();
	std::cout << "Hands Played: " << hands_played << std::endl;
	
	if (hands_played <= 0)
		return;

	balance = player->get_balance();
	advantage = balance / player->get_hands_played();
	std::cout << "Final Balance: " << to_currency(balance) << std::endl;
	std::cout << "Player Advantage: " << std::setprecision(4) 
			  << advantage*100 << "%" << std::endl;
}

