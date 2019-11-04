_ = "\n   "
redirected_print = print
def print(*args, **kwargs):
    kwargs["end"] = "\n\n"
    redirected_print(*args, **kwargs)

class MetaTable(type):

    def __prepare__(cls, *args, **kwargs):
        print("metaclass prepare:", _, cls, _, args, _, kwargs)
        return {}

    def __call__(cls, *args, **kwargs):
        print("metaclass call:", _, cls, _, args, _, kwargs)
        return super().__call__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        print("metaclass new:", _, cls, _, args, _, kwargs)
        instance = type.__new__(cls, *args)
        return instance


class Table(object, metaclass=MetaTable):

    def __new__(cls, *args, **kwargs):
        print("class new:", _, cls, _, args, _, kwargs)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        print("class init:", _, self, _, args, _, kwargs)
        [ setattr(self, k, kwargs[k]) for k in kwargs ]


class User(Table):

    firstName = "Grace"
    age = 20

u = User(firstName="John", age=13)
print(u.age)
