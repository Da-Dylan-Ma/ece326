# Field name has underscore.

import orm

class Person(orm.Table):
    firstName = orm.String()
    last_name = orm.String()
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<Person: %s %s>"%(self.firstName, self.lastName)

