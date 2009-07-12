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
ResourceDoesNotExistError = "ResourceDoesNotExistError"
NoDataError = "NoDataError"

CreateEventError = "CreateEventError"
CreatePermissionError = "CreatePermissionError"

AlreadySubscribedError = "AlreadySubscribedError"
NotSubscribedError = "NotSubscribedError"

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
    def loggedInFn(*args, **kwargs):
        loggedInUser = helper.getLoggedInUser()
        if not loggedInUser:
            return error("User not logged in", UserNotLoggedInError)
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
                return error("Resource %s is not of type %s" % (rid, type))
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
            return error(errorStr, errorType)
        else:
            return func(*args, **kwargs)
    return existsFn

# Resource
# ==============================================================================

class ResourceController:
    def primaryKey(self):
        return "id"

    def resolveSource(self, id):
        return id

    def resourceDoesNotExistString(self, id):
        return ("Resource %s does not exist" % id)

    def resourceDoesNotExistType(self):
        return ResourceDoesNotExistError

 
# User
# ==============================================================================

class UserController(ResourceController):
    def primaryKey(self):
        return "userName"

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
    @exists
    @loggedin
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
    @exists
    @loggedin
    def delete(self, userName):
        if not user.read(userName):
            return error("User %s does not exist" % userName, UserDoesNotExistError)
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and user.canDelete(user.idForName(userName),
                                           loggedInUser["_id"]):
            if user.idForName(userName) == loggedInUser["_id"]:
                helper.setLoggedInUser(None)
            user.delete(userName)
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
        jsonData = helper.getRequestBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            theData['createdBy'] = loggedInUser.get("_id")
            return data(shift.create(theData))
        else:
            return error("No data for shift.", NoDataError)

    @jsonencode
    @exists
    @shiftType
    def read(self, id):
        allowed = shift.isPublic(id)
        if not allowed:
            loggedInUser = helper.getLoggedInUser()
            if loggedInUser and shift.canRead(id, loggedInUser.get("_id")):
                return data(shift.read(id))
            else:
                return error("Operation not permitted. You don't have permission to view this shift.", PermissionError)
        else:
            return data(shift.read(id))

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.read(id)
        if loggedInUser and shift.canUpdate(id, loggedInUser['_id']):
            shift.update(helper.getRequestBody())
            return ack
        else:
            return error("Operation not permitted. You don't have permission to update this shift.", PermissionError)
        

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.read(id)
        if loggedInUser and shift.canDelete(id, loggedInUser['_id']):
            shift.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this shift.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def publish(self, id):
        loggedInUser = helper.getLoggedInUser()
        publishData = json.loads(helper.getRequestBody())
        theShift = shift.read(id)
        if loggedInUser and shift.canPublish(id, loggedInUser['_id']):
            shift.publish(id, publishData)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def unpublish(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.read(id)
        if loggedInUser and shift.canUnpublish(id, loggedInUser['_id']):
            shift.unpublish(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.", PermissionError)

    @jsonencode
    def comments(self, id):
        pass

# Event
# ==============================================================================

class EventController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getResponseBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            streamId = theData["streamId"]
            if not streamId:
                return error("You did not specify a stream to post to", CreateEventError)
            if stream.canPost(streamId, loggedInUser["_id"]):
                return data(event.create(theData))
        else:
            return error("No data for event.", NoDataError)

    @jsonencode
    @exists
    @eventType
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and event.canRead(id, loggedInUser["_id"]):
            return data(event.read(id))
        else:
            return error("Operation not permitted. You don't have permission to read this event.", PermissionError)

    @jsonencode
    @exists
    @eventType
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if event.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(event.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this event.", PermissionError)

    @jsonencode
    @exists
    @eventType
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        if event.canDelete(id, loggedInUser["_id"]):
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
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            theData['createdBy'] = loggedInUser.get("_id")
            return data(stream.create(theData))
        else:
            return error("No data for stream.", NoDataError)

    @jsonencode
    @exists
    @streamType
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if stream.canRead(id, loggedInUser["_id"]):
            return data(stream.read(id))
        else:
            return error("Operation not permitted. You don't have permission to view this stream.", PermissionError)

    @jsonencode
    @exists
    @streamType
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if stream.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(stream.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this stream", PermissionError)

    @jsonencode
    @exists
    @streamType
    @loggedin
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        if stream.canDelete(id, loggedInUser["_id"]):
            stream.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this stream.", PermissionError)

    @jsonencode
    @exists
    @streamType
    @loggedin
    def subscribe(self, id):
        loggedInUser = helper.getLoggedInUser()
        if stream.canSubscribe(id, loggedInUser["_id"]):
            if user.isSubscribed(loggedInUser["_id"], id):
                return error("You are already subscribed to that stream.", AlreadySubscribedError)
            else:
                stream.subscribe(id, loggedInUser["_id"])
                return ack
        else:
            return error("Operation not permitted. You don't have permission to subscribe to this stream.", PermissionError)

    @jsonencode
    @exists
    @streamType
    @loggedin
    def unsubscribe(self, id):
        loggedInUser = helper.getLoggedInUser()
        if user.isSubscribed(id):
            stream.unsubscribe(id, loggedInUser["_id"])
            return ack
        else:
            return error("You are not subscribed to that stream.", NotSubscribedError)


    @jsonencode
    def invite(self, id, userName):
        pass

    @jsonencode
    @exists
    @streamType
    @loggedin
    def add(self, id, userName):
        loggedInUser = helper.getLoggedInUser()
        if stream.canAdmin(id, loggedInUser["_id"]):
            otherId = user.idForName(userName)
            if user.isSubscribed(otherId, id):
                return error("User %s is already subscribed to that stream." % userName, AlreadySubscribedError)
            else:
                stream.invite(id, loggedInUser["_id"], otherId)
                return ack
        else:
            return error("Operation not permitted. You don't have permission to subscribe to this stream.", PermissionError)


    @jsonencode
    def remove(self, id, userName):
        return "remove %s from %s" % (userName, id)

    @jsonencode
    def block(self, id, userName):
        pass

    @jsonencode
    def post(self, id):
        pass

    @jsonencode
    @exists
    @streamType
    @loggedin
    def permissions(self, id):
        loggedInUser = helper.getLoggedInUser()
        if stream.canAdmin(id, loggedInUser["_id"]):
            return data(stream.permissions(id))
        else:
            return error("Operation not permitted. You don't have permission to view permssions on this stream.", PermissionError)
        


# Permission
# ==============================================================================

class PermissionController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getResponseBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            streamId = theData["streamId"]
            if not streamId:
                return error("You did not specify a stream to create a permission for", CreatePermissionError)
            if stream.canAdmin(streamId, loggedInUser["_id"]):
                return data(permission.create(theData))
        else:
            return error("No data for permission.", NoDataError)

    @jsonencode
    @exists
    @permissionType
    @loggedin    
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if permission.canRead(id, loggedInUser["_id"]):
            return data(permission.read(id))
        else:
            return error("Operation not permitted. You don't have permission to view this permission.", PermissionError)

    @jsonencode
    @exists
    @permissionType
    @loggedin
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and permission.canUpdate(id, loggedInUser["_id"]):
            data = helper.getResponseBody()
            return data(permission.update(data))
        else:
            return error("Operation not permitted. You don't have permission to update this permission.", PermissionError)

    @jsonencode
    @exists
    @permissionType
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
    permission = PermissionController()
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

    d.connect(name="userMessages", route="user/:userName/messages", controller=user, action="messages",
              conditions=dict(method="GET"))
    d.connect(name="userShifts", route="user/:userName/shifts", controller=user, action="shifts",
              conditions=dict(method="GET"))

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

    d.connect(name="shiftPublish", route="shift/:id/publish", controller=shift, action="publish",
              conditions=dict(method="POST"))
    d.connect(name="shiftUnpublish", route="shift/:id/unpublish", controller=shift, action="unpublish",
              conditions=dict(method="POST"))

    d.connect(name="shiftComments", route="shift/:id/comments", controller=shift, action="comments",
              conditions=dict(method="POST"))

    d.connect(name="shifts", route="shifts", controller=shifts, action="shifts",
              conditions=dict(method="GET"))

    # Stream Routes
    d.connect(name="streamCreate", route="stream", controller=stream, action="create",
              conditions=dict(method="POST"))
    d.connect(name="streamRead", route="stream/:id", controller=stream, action="read",
              conditions=dict(method="GET"))
    d.connect(name="streamUpdate", route="stream/:id", controller=stream, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="streamDelete", route="stream/:id", controller=stream, action="read",
              conditions=dict(method="DELETE"))

    d.connect(name="streamSubscribe", route="stream/:id/subscribe", controller=stream, action="subscribe",
              conditions=dict(method="POST"))
    d.connect(name="streamUnsubscribe", route="stream/:id/unsubscribe", controller=stream, action="unsubscribe",
              conditions=dict(method="POST"))

    d.connect(name="streamInvite", route="stream/:id/invite/:userName", controller=stream, action="invite",
              conditions=dict(method="POST"))
    d.connect(name="streamAdd", route="stream/:id/add/:userName", controller=stream, action="add",
              conditions=dict(method="POST"))
    d.connect(name="streamRemove", route="stream/:id/remove/:userName", controller=stream, action="remove",
              conditions=dict(method="POST"))
    d.connect(name="streamBlock", route="stream/:id/block/:userName", controller=stream, action="block",
              conditions=dict(method="POST"))

    d.connect(name="streamPost", route="stream/:id/post", controller=stream, action="post",
              conditions=dict(method="POST"))

    # Event Routes
    d.connect(name="eventRead", route="event/:id", controller=event, action="read",
              conditions=dict(method="GET"))
    d.connect(name="eventUpdate", route="event/:id", controller=event, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="eventDelete", route="event/:id", controller=event, action="delete",
              conditions=dict(method="DELETE"))

    # Permission Routes
    d.connect(name="permissionCreate", route="permission", controller=permission, action="create",
              conditions=dict(method="POST"))
    d.connect(name="permissionRead", route="permission/:id", controller=permission, action="read",
              conditions=dict(method="GET"))
    d.connect(name="permissionUpdate", route="permission/:id", controller=permission, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="permissionDelete", route="permission/:id", controller=permission, action="read",
              conditions=dict(method="DELETE"))

    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))


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
