# 
# Makefile 
#
# Assignment 1 Makefile
#
# University of Toronto
# 2019

PROG=asst1
SOURCE=$(wildcard *.cpp)
OBJECT=$(SOURCE:.cpp=.o)
DEPEND=depend.mk
CFLAGS=-Wall -Wextra -Werror -g -std=gnu++11
CC=g++

all: $(DEPEND) $(PROG)

$(PROG): $(OBJECT)
	$(CC) $(CFLAGS) $^ -o $@

# both source and header files
$(DEPEND): $(wildcard *.cpp *.h)
	$(CC) -MM $(SOURCE) > $(DEPEND)
	
.cpp.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $< -o $@

.PHONY: clean	
clean:
	rm -f *.o *.exe tester.* $(DEPEND) $(PROG) 
	
ifeq ($(DEPEND),$(wildcard $(DEPEND)))
include $(DEPEND)
endif
