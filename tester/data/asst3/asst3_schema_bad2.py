# Choices value is not the correct type.

import orm

class Person(orm.Table):
    firstName = orm.String()
    lastName = orm.String(choices=["Hinton", 3])
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<Person: %s %s>"%(self.firstName, self.lastName)

