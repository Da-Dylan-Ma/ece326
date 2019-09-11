 /*
 * shoe.h
 *
 * Abstract interface for a shoe
 *
 * Note: you may not change this file
 *
 * University of Toronto
 * Fall 2019
 */
 
#ifndef SHOE_H
#define SHOE_H

class Config;

class Shoe {	
public:
	Shoe() {}
    virtual ~Shoe() {}

	/*
	 * Returns the next card in the shoe
	 */
	virtual char pop()=0;
	
	/*
	 * Returns true if the shoe is over
	 */
	virtual bool over() const=0;
	
	
	
	static Shoe * factory(const Config * config);
};

#endif /* SHOE_H */

