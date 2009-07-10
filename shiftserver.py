import os
import time
import cherrypy
import routes
import md5
import email
import simplejson as json

from decorators import jsonencode
from decorators import simple_decorator

import core
import models.user as user
import models.shift as shift
import models.stream as stream
import models.event as event
import models.permission as permission
import models.groups as groups

# Return types
# ==============================================================================

ack = {"message":"ok"}

def error(msg, type=None):
    err = {"error":msg}
    if type:
        err["type"] = type
    return err

def data(d):
    return {"data":d}

def message(msg):
    return {"message":msg}

# Error types
# =============================================================================

AlreadyLoggedInError = "AlreadyLoggedInError"
AlreadyLoggedOutError = "AlreadyLoggedOutError"
InvalidUserNameError = "InvalidUserNameError"
IncorrectPasswordError = "IncorrectPasswordError"
UserNotLoggedInError = "UserNotLoggedInError"

NoEmailError = "NoEmailError"
MissingUserNameError = "MissingUserNameError"
ShortUserNameError = "ShortUserNameError"
UserNameAlreadyExistsError = "UserNameAlreadyExistsError"
MissingPasswordError = "MissingPasswordError"
MissingPasswordVerifyError = "MissingPasswordVerifyError"
PasswordMatchError = "PasswordMatchError"
FollowError = "FollowError"

UserDoesNotExistError = "UserDoesNotExistError"
PermissionError = "PermissionError"
ResourceDoesNotExistsError = "ResourceDoesNotExistsError"

# Utils
# =============================================================================

def md5hash(str):
    m = md5.new()
    m.update(str)
    return m.hexdigest()

# Helper
# ==============================================================================

class Helper:
    def setLoggedInUser(self, data):
        cherrypy.session['loggedInUser'] = data

    def getLoggedInUser(self):
        return cherrypy.session.get('loggedInUser')

    def getRequestBody(self):
        return cherrypy.request.body.read()
helper = Helper()

# Decorators
# ==============================================================================

@simple_decorator
def loggedin(func):
    """
    Verify a user is logged in before running a controller action.
    """
    def afn(*args, **kwargs):
        loggedInUser = helper.getLoggedInUser()
        if not loggedInUser:
            return error("User not logged in", UserNotLoggedInError)
        return func(*args, **kwargs)
    return afn

def verifyDecoratorGenerator(type):
    """
    Generates a type verifier. This is because some resources take
    generic db ids. Should only be applied to methods of a controller
    where the first parameter is the resource (document) id.
    """
    def verifyDecorator(func):
        def afn(*args, **kwargs):
            db = core.connect()
            rid = kwargs["id"]
            if db[rid]["type"] != type:
                return error("Resource %s is not of type %s" % (rid, type))
            return func(*args, **kwargs)
        return afn
    return verifyDecorator

shiftType = verifyDecoratorGenerator("shift")
userType = verifyDecoratorGenerator("user")
streamType = verifyDecoratorGenerator("stream")
eventType = verifyDecoratorGenerator("event")
permissionType = verifyDecoratorGenerator("permission")

def exists(func):
    def afn(*args, **kwargs):
        db = core.connect()
        instance = args[0]
        id = kwargs.values()[0]
        
        resolver = getattr(instance, "resolveResource")
        if resolver:
            id = resolver(id)

        if (not id) or (not db[id]):
            fnA = getattr(instance, "resourceDoesNotExistString")
            errorStr = (fnA and fnA(id)) or ("Resource %s does not exist" % id)
            fnB = getattr(instance, "resourceDoesNotExistType")
            errorType = (fnB and fnB()) or ResourceDoesNotExistsError
            return error(errorStr, errorType)
        else:
            return func(*args, **kwargs)
    return afn

# Resource
# ==============================================================================

class ResourceController:
    def resourceExists(self, id):
        db = core.connect()
        if db[id]:
            return True
        else:
            return False
 
# User
# ==============================================================================

class UserController(ResourceController):

    def resolveResource(self, userName):
        theUser = user.read(userName)
        return (theUser and theUser["_id"])

    def resourceDoesNotExistString(self, userName):
        return "User %s does not exist" % userName
    
    def resourceDoesNotExistType(self):
        return UserDoesNotExistError

    def isValid(self, data):
        if not data.get("email"):
            return (False, "Please specify your email address.", NoEmailError)
        userName = data.get("userName")
        if not userName:
            return (False, "Please enter a user name.", MissingUserNameError)
        if len(userName) < 6:
            return (False, "Your user name should be at least 6 characters long.", ShortUserNameError)
        if not user.nameIsUnique(userName):
            return (False, "That user name is taken, please choose another.", UserNameAlreadyExistsError)
        if not data.get("password"):
            return (False, "Please supply a password.", MissingPasswordError)
        if not data.get("passwordVerify"):
            return (False, "Please enter your password twice.", MissingPasswordVerifyError)
        if data.get("password") != data.get("passwordVerify"):
            return (False, "Passwords do not match.", PasswordMatchError)
        return (True, data, None)

    @jsonencode
    def join(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            return error("You are logged in. You cannot create an account.", AlreadyLoggedInError)

        theData = json.loads(helper.getRequestBody())

        valid, msg, errType = self.isValid(theData)
        result = None
        if valid:
            theData["password"] = md5hash(theData["password"])
            del theData["passwordVerify"]
            id = user.create(theData)
            theUser = user.getById(id)
            helper.setLoggedInUser(theUser)
            return data(theUser)
        else:
            return error(msg, errType)

    @jsonencode
    @exists
    def read(self, userName):
        if not user.read(userName):
            return error("User %s does not exist" % userName, UserDoesNotExistError)
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and user.canReadFull(user.idForName(userName),
                                             loggedInUser["_id"]):
            return data(user.readFull(userName).copy())
        else:
            return data(user.read(userName).copy())


    @jsonencode
    @loggedin
    @exists
    def update(self, userName):
        if not user.read(userName):
            return error("User %s does not exist" % userName, UserDoesNotExistError)
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and user.canUpdate(user.idForName(userName),
                                           loggedInUser["_id"]):
            shift.update(helper.getRequestBody())
            return ack
        else:
            return error("Operation not permitted. You don't have permission to update this account.")

    @jsonencode
    @loggedin
    @exists
    def delete(self, userName):
        if not user.read(userName):
            return error("User %s does not exist" % userName, UserDoesNotExistError)
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and user.canDelete(user.idForName(userName),
                                           loggedInUser["_id"]):
            user.delete(userName)
            helper.setLoggedInUser(None)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this account.")

    @jsonencode
    def query(self):

        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            return loggedInUser
        else:
            return message("No logged in user")

    @jsonencode
    def login(self, userName, password):
        loggedInUser = helper.getLoggedInUser()
        if not loggedInUser:
            theUser = user.readFull(userName)

            if not theUser:
                return error("Invalid user name.", InvalidUserNameError)

            if theUser and (theUser['password'] == md5hash(password)):
                helper.setLoggedInUser(theUser)
                user.updateLastSeen(userName)
                return data(theUser)
            else:
                return error("Incorrect password.", IncorrectPasswordError)
        else:
            return error("Already logged in.", AlreadyLoggedInError)

    @jsonencode
    def logout(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            user.updateLastSeen(loggedInUser["userName"])
            helper.setLoggedInUser(None)
            return ack
        else:
            return error("No user logged in.", AlreadyLoggedOutError)

    @jsonencode
    @exists
    def resetPassword(self, userName):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            # TODO: generate random 8 character password update user and email
            return ack
        else:
            return error("No user logged in.", UserNotLoggedInError)

    @jsonencode
    @loggedin
    @exists
    def follow(self, userName):
        loggedInUser = helper.getLoggedInUser()
        lname = loggedInUser["userName"]
        if lname == userName:
            return error("You cannot follow yourself.", FollowError)
        user.follow(lname, userName)
        return ack

    @jsonencode
    @loggedin
    @exists
    def unfollow(self, userName):
        loggedInUser = helper.getLoggedInUser()
        lname = loggedInUser["userName"]
        if lname == userName:
            return error("You cannot unfollow yourself.", FollowError)
        user.unfollow(lname, userName)
        return ack


# Shift
# ==============================================================================

class ShiftController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            theData = json.loads(helper.getRequestBody())
            theData['createdBy'] = loggedInUser.get("_id")
            return data(shift.create(theData))
        else:
            return error("Operation not permitted. You are not logged in", PermissionError)

    @jsonencode
    @shiftType
    @exists
    def read(self, id):
        allowed = shift.isPublic(id)
        if not allowed:
            loggedInUser = helper.getLoggedInUser()
            if loggedInUser and shift.canRead(id, loggedInUser.get("_id")):
                return data(shift.get(id))
            else:
                return error("Operation not permitted. You don't have permission to view this shift.", PermissionError)
        else:
            return data(shift.get(id))

    @jsonencode
    @shiftType
    @exists
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and shift.canUpdate(id, loggedInUser['_id']):
            shift.update(helper.getRequestBody())
            return ack
        else:
            return error("Operation not permitted. You don't have permission to update this shift.", PermissionError)

    @jsonencode
    @shiftType
    @exists
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and shift.canDelete(id, loggedInUser['_id']):
            shift.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this shift.", PermissionError)

    @jsonencode
    @shiftType
    @exists
    @loggedin
    def publish(self, id):
        loggedInUser = helper.getLoggedInUser()
        publishData = json.loads(helper.getRequestBody())
        theShift = shift.get(id)
        if loggedInUser and shift.canPublish(id, loggedInUser['_id']):
            shift.publish(id, publishData)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.", PermissionError)

    @jsonencode
    @shiftType
    @exists
    @loggedin
    def unpublish(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and shift.canUnpublish(id, loggedInUser['_id']):
            shift.unpublish(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.", PermissionError)

# Event
# ==============================================================================

class EventController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        pass

    @jsonencode
    @eventType
    @exists
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and event.canRead(id, loggedInUser["_id"]):
            return data(event.read(id))
        else:
            return error("Operation not permitted. You don't have permission to read this event.", PermissionError)

    @jsonencode
    @eventType
    @exists
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and event.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(event.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this event.", PermissionError)

    @jsonencode
    @eventType
    @exists
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and event.canDelete(id, loggedInUser["_id"]):
            event.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this event.", PermissionError)

# Stream
# ==============================================================================

class StreamController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        pass

    @jsonencode
    @streamType
    @exists
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and stream.canRead(id, loggedInUser["_id"]):
            return data(stream.read(id))
        else:
            return error("Operation not permitted. You don't have permission to view this stream.", PermissionError)

    @jsonencode
    @streamType
    @exists
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and stream.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(stream.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this stream", PermissionError)

    @jsonencode
    @streamType
    @exists
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and stream.canDelete(id, loggedInUser["_id"]):
            stream.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this stream.", PermissionError)

    def comments(self, shiftId):
        pass

    def privateStram(self, userId):
        pass

# Permission
# ==============================================================================

class PermissionController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        pass

    @jsonencode
    @permissionType
    @exists
    @loggedin    
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and permission.canRead(id, loggedInUser["_id"]):
            return data(permission.read(id))
        else:
            return error("Operation not permitted. You don't have permission to view this permission.", PermissionError)

    @jsonencode
    @permissionType
    @exists
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and permission.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(permission.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this permission.", PermissionError)

    @jsonencode
    @permissionType
    @exists
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and permission.canDelete(id, loggedInUser["_id"]):
            permission.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this permission.", PermissionError)

# Aggregates
# ==============================================================================

class ShiftsController(ResourceController):
    @jsonencode
    def read(self, userName):
        return data(shift.byUserName(userName))

    def feed(self, userName):
        pass


class GroupsController(ResourceController):
    @jsonencode
    def read(self, id):
        # return only public groups
        return data(groups.inGroup(int(id)))


# Main
# ==============================================================================

class RootController:
    def read(self):
        return "ShiftSpace Server 1.0"


def initRoutes():
    root = RootController()
    user = UserController()
    shift = ShiftController()
    stream = StreamController()
    event = EventController()
    shifts = ShiftsController()
    group = GroupsController()

    d = cherrypy.dispatch.RoutesDispatcher()

    # Root
    d.connect(name="root", route="", controller=root, action="read")

    # User Routes
    d.connect(name="userLogin", route="login", controller=user, action="login",
              conditions=dict(method="POST"))
    d.connect(name="userLogout", route="logout", controller=user, action="logout",
              conditions=dict(method="POST"))
    d.connect(name="userQuery", route="query", controller=user, action="query",
              conditions=dict(method="GET"))
    d.connect(name="userJoin", route="join", controller=user, action="join",
              conditions=dict(method="POST"))

    d.connect(name="userRead", route="user/:userName", controller=user, action="read",
              conditions=dict(method="GET"))
    d.connect(name="userUpdate", route="user/:userName", controller=user, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="userDelete", route="user/:userName", controller=user, action="delete",
              conditions=dict(method="DELETE"))

    d.connect(name="userFollow", route="follow/:userName", controller=user, action="follow",
              conditions=dict(method="POST"))
    d.connect(name="userUnfollow", route="unfollow/:userName", controller=user, action="unfollow",
              conditions=dict(method="POST"))

    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              conditions=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              conditions=dict(method="GET"))
    d.connect(name="shiftUpdate", route="shift/:id", controller=shift, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="shiftDelete", route="shift/:id", controller=shift, action="delete",
              conditions=dict(method="DELETE"))

    d.connect(name="shiftsPublish", route="publish/:id", controller=shift, action="publish",
              conditions=dict(method="POST"))
    d.connect(name="shiftsUnpublish", route="unpublish/:id", controller=shift, action="unpublish",
              conditions=dict(method="POST"))

    d.connect(name="shiftsRead", route="shifts/:userName", controller=shifts, action="read",
              conditions=dict(method="GET"))

    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))

    # Stream Routes
    d.connect(name="streamRead", route="stream/:id", controller=stream, action="read",
              conditions=dict(method="GET"))

    # Event Routes

    return d


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes(),
                 'tools.sessions.on': True,
                 'tools.sessions.storage_type': "file",
                 'tools.sessions.storage_path':"/Users/davidnolen/Sites/shiftserver/sessions",
                 'tools.sessions.timeout': 60}}


if __name__ == "__main__":
    cherrypy.config.update({'server.socket_port':8080})
    # TODO: The following value should be read from an environment file - David 7/4/09
    app = cherrypy.tree.mount(root=None, script_name='/~davidnolen/shiftspace/shiftserver', config=appconf)
    cherrypy.quickstart(app)
