import orm

class User(orm.Table):
    firstName = orm.String(blank=True)
    lastName = orm.String(blank=True)
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

class Cash(orm.Table):
    value = orm.Float()
    currency = orm.String()
    owner = orm.Foreign(User)

class Account(orm.Table):
    user = orm.Foreign(User)
    type = orm.String()
    balance = orm.Foreign(Cash)
