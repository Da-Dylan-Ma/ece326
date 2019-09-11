/*
 * shoe.cpp
 *
 * Member functions for Shoe-related classes
 *
 * Note: you may not change this file
 *
 * University of Toronto
 * Fall 2019
 */

#include "shoe.h"
#include "config.h"
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cerrno>
#include <cassert>

#define CUT_DEPTH 26

class InfiniteShoe : public Shoe {
	FILE * file;
	
public:
	/*
	 * seed: if negative, uses current time as random seed
	 */
	InfiniteShoe(long seed=-1);

	int open(const char * filename);
	virtual char pop() override;
	virtual bool over() const {
		return false;
	}
	virtual ~InfiniteShoe();
};

class FileShoe : public Shoe {	
	FILE * file;
	long size;
	
public:
	FileShoe() : Shoe(), file(nullptr), size(0) {}

	int open(const char * filename);
	virtual char pop() override;
	virtual bool over() const;
	virtual ~FileShoe();
};

static const char cards[] = { 
	'A', '2', '3', '4', '5', '6', '7', 
    '8', '9', 'T', 'J', 'Q', 'K' 
};

static const int num_cards = sizeof(cards)/sizeof(char);

InfiniteShoe::InfiniteShoe(long seed) : Shoe(), file(nullptr)
{
	if (seed < 0)
		srand(time(NULL));
	else
		srand((unsigned int)seed);
}

InfiniteShoe::~InfiniteShoe()
{
	if (file != nullptr) {
		int i;
		for (i = 0; i < CUT_DEPTH; i++)
			pop();
		fclose(file);
	}
}

int InfiniteShoe::open(const char * filename)
{
	if (file != nullptr)
		fclose(file);

	file = fopen(filename, "wt");
	if (file == nullptr)
		return -errno;
	fprintf(stderr, "Recording shoe to %s.\n", filename);
	
	return 0;
}

char InfiniteShoe::pop()
{
	char c = cards[rand()%num_cards];
	
	if (file != nullptr)
		fputc(c, file);

	return c;
}

int FileShoe::open(const char * filename)
{
	if (file != nullptr)
		fclose(file);

	size = 0;
	file = fopen(filename, "rt");
	if (file == nullptr)
		return -errno;
	
	fseek(file, 0, SEEK_END);
	size = (long)ftell(file);
	fseek(file, 0, SEEK_SET);
	return 0;
}

template<typename T> 
bool is_in(T & a, T b) {
	return a == b;
}

template<typename T, typename... Args> 
bool is_in(T & a, T b, Args... args) {
	return a == b || is_in(a, args...);
}

char FileShoe::pop() 
{
	char c;
	
	assert(file);
	while (size > 0) {
		c = getc(file);
		size--;
		if (c >= '2' && c <= '9')
			return c;
		if (is_in(c, 'A', 'T', 'J', 'Q', 'K'))
			return c;
	}
	
	assert(false);
	return c;
}

bool FileShoe::over() const
{
	return size < CUT_DEPTH;
}

FileShoe::~FileShoe()
{
	if (file != nullptr)
		fclose(file);
}

Shoe * Shoe::factory(const Config * config)
{
	InfiniteShoe * shoe;
	
	if (config->shoe_file != nullptr) {
		FileShoe * shoe = new FileShoe();
		
		if (shoe->open(config->shoe_file) < 0) {
			delete shoe;
			return nullptr;
		}
		
		return shoe;
	}

	shoe = new InfiniteShoe(config->random_seed);
	if (config->record_file != nullptr) {
		if (shoe->open(config->record_file) < 0) {
			delete shoe;
			return nullptr;
		}
	}
	
	return shoe;
}
