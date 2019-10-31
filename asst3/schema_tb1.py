import orm

class User(orm.Table):
    firstName = orm.String(blank=True)
    lastName = orm.String(blank=True)
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<User: %s %s>"%(self.firstName, self.lastName)

class Account(orm.Table):
    user = orm.Foreign(User)
    type = orm.String(choices=["Savings", "Chequing",], default="Chequing")
    balance = orm.Float(blank=True)

    def __repr__(self):
        return "<Account: %s's %s>"%(self.user.firstName, self.type)
