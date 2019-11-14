# Field name uses reserved word.

import orm

class Person(orm.Table):
    firstName = orm.String()
    pk = orm.String()
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<Person: %s %s>"%(self.firstName, self.lastName)

