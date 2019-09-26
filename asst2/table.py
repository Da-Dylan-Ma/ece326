#!/usr/bin/python3
#
# table.py
#
# Implements a two-dimension table where all cells must be of same type
#
# Note: completed
#

from collections import defaultdict
from collections.abc import Sized
# Sized requires subclasses to implement __len__()


class Table:
    #
    # Initializes an instance of Table class
    #
    # celltype: type of each cell in table
    # xlabels: labels of x-axis
    # ylables: labels of y-axis
    # unit: unit of each cell (printed as suffix)
    #
    def __init__(self, celltype, xlabels, ylabels, unit=""):
        if not isinstance(celltype, type):
            raise TypeError("celltype must be a type (e.g. str, float)")
        self.celltype = celltype
        self.xlabels = tuple(xlabels)
        self.ylabels = tuple(ylabels)
        self.unit = unit
        self.data = defaultdict(lambda: defaultdict(lambda: None))
        # using defaultdict since no extra code for initialization

    #
    # "private" member function to validate key
    #
    def _validate_key(self, key):
        if not isinstance(key, Sized):
            raise TypeError("key must be a sized container")
        if len(key) != 2:
            raise KeyError("key must have exactly two elements")
        # unpack key to row and column
        row, col = key
        if row not in self.ylabels:
            raise KeyError("%s is not a valid y-label"%str(row))
        if col not in self.xlabels:
            raise KeyError("%s is not a valid x-label"%str(col))
        return row, col

    #
    # Overloads index operator for assigning to a cell
    #
    # key: key of the cell
    # value: value of the cell (must be of type 'celltype')
    #
    def __setitem__(self, key, value):
        if not isinstance(value, self.celltype):
            raise TypeError("value must be of type %s"%(self.celltype.__name__))
        row, col = self._validate_key(key)
        self.data[row][col] = value

    #
    # Overloads index operator for retrieving a value from a cell
    #
    # key: key of the cell
    #
    def __getitem__(self, key):
        row, col = self._validate_key(key)
        return self.data[row][col]

    #
    # Overloads index operator for deleting a cell's value. You should
    # set the cell's value back to None
    #
    # key: key of the cell
    #
    def __delitem__(self, key):
        row, col = self._validate_key(key)
        self.data[row][col] = None
