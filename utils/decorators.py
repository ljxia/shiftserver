import simplejson as json
import models.core as core
import returnTypes

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
    """
    Verify a user is logged in before running a controller action.
    """
    def loggedInFn(*args, **kwargs):
        loggedInUser = helper.getLoggedInUser()
        if not loggedInUser:
            return returnTypes.error("User not logged in", UserNotLoggedInError)
        return func(*args, **kwargs)
    return loggedInFn

def verifyDecoratorGenerator(type):
    """
    Generates a type verifier. This is because some resources take
    generic db ids. Should only be applied to methods of a controller
    where the first parameter is the resource (document) id.
    """
    def verifyDecorator(func):
        def verifyFn(*args, **kwargs):
            db = core.connect()
            rid = kwargs["id"]
            if db[rid]["type"] != type:
                return returnTypes.error("Resource %s is not of type %s" % (rid, type))
            return func(*args, **kwargs)
        return verifyFn
    return verifyDecorator

shiftType = verifyDecoratorGenerator("shift")
userType = verifyDecoratorGenerator("user")
streamType = verifyDecoratorGenerator("stream")
eventType = verifyDecoratorGenerator("event")
permissionType = verifyDecoratorGenerator("permission")

def exists(func):
    """
    Ensure that a the resource actually exists before trying to serve it.
    """
    def existsFn(*args, **kwargs):
        db = core.connect()
        instance = args[0]

        primaryKey = getattr(instance, "primaryKey")()
        id = kwargs[primaryKey]

        resolver = None
        
        if hasattr(instance, "resolveResource"):
            resolver = getattr(instance, "resolveResource")

        if resolver:
            id = resolver(id)

        if (not id) or (not db.get(id)):
            errorStr = ""
            errorType = ""
            if hasattr(instance, "resourceDoesNotExistString"):
                errorStr = getattr(instance, "resourceDoesNotExistString")(id)
            if hasattr(instance, "resourceDoesNotExistType"):
                errorType = getattr(instance, "resourceDoesNotExistType")()
            return returnTypes.error(errorStr, errorType)
        else:
            return func(*args, **kwargs)
    return existsFn
