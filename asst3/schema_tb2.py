import orm

class User(orm.Table):
    firstName = orm.String(blank=True)
    lastName = orm.String(blank=True)
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)
    account = orm.Foreign(Account)

class Cash(orm.Table):
    value = orm.Float()
    currency = orm.String()

class Account(orm.Table):
    user = orm.Foreign(User)
    type = orm.String()
    balance = orm.Foreign(Cash)
