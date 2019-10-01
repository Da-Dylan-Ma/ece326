#
# Makefile
#
# Assignment 1 Makefile
#
# University of Toronto
# 2019
#
# Added Windows clean

PROG=asst1
SOURCE=$(wildcard *.cpp)
OBJECT=$(SOURCE:.cpp=.o)
DEPEND=depend.mk
CFLAGS=-Wall -Wextra -Werror -g -std=gnu++11
CC=g++
ifeq ($(OS),Windows_NT)
	CMD=del /s
else
	CMD=rm -rf
endif

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
	$(CMD) *.o *.exe tester.* $(DEPEND) $(PROG)

ifeq ($(DEPEND),$(wildcard $(DEPEND)))
include $(DEPEND)
endif
