import simplejson as json

def simple_decorator(decorator):
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

@simple_decorator
def jsonencode(func):
    def afn(*args, **kwargs):
        return json.dumps(func(*args, **kwargs))
    return afn

@simple_decorator
def loggedin(func):
    def afn(*args, **kwargs):
        loggedInUser = helper.getLoggedInUser()
        if not loggedInUser:
            return error("User not logged in", UserNotLoggedInError)
        return func(*args, **kwargs)
    return afn
