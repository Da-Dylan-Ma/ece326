import orm

if orm.DateTime.implemented:
    from datetime import datetime

class User(orm.Table):
    firstName = orm.String()
    lastName = orm.String()
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<User: %s %s>"%(self.firstName, self.lastName)
    
class Account(orm.Table):   
    user = orm.Foreign(User)
    type = orm.String(choices=["Normal", "Special",], default="Normal")
    balance = orm.Float(blank=True)
    
    def __repr__(self):
        return "<Account: %s's %s>"%(self.user.firstName, self.type)

if orm.Coordinate.implemented:
    class City(orm.Table):
        location = orm.Coordinate(blank=True)
        name = orm.String()
        
        def __repr__(self):
            return "<City: %s>"%(self.name)
            
if orm.DateTime.implemented:
    class Event(orm.Table):
        location = orm.Foreign(City)
        start = orm.DateTime(default=datetime.now)
        end = orm.DateTime(blank=True)
        
        def __repr__(self):
            return "<Event: %s>"%(self.location)
