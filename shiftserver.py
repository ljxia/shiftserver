import os
import time
import cherrypy
import routes
import md5
import email
import simplejson as json

from decorators import jsonencode

import models.user as user
import models.shift as shift
import models.stream as stream
import models.event as event
import models.permission as permission
import models.groups as groups

# Return types
# ==============================================================================

ack = {"message":"ok"}

def error(msg):
    return {"error":msg}

def data(d):
    return {"data":d}

def message(msg):
    return {"message":msg}

# Utils
# =============================================================================

def hash(str):
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


# Resource
# ==============================================================================

class Resource:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def updateField(self, id, key, value):
        pass
    def delete(self, id):
        pass

# User
# ==============================================================================

class User:
    def isValid(self, data):
        if not data.get("email"):
            return (False, "Please specify your email address.")
        userName = data.get("userName")
        if not userName:
            return (False, "Please enter a user name.")
        if len(userName) < 6:
            return (False, "Your user name should be at least 6 characters long.")
        if not user.nameIsUnique(userName):
            return (False, "That user name is taken, please choose another.")
        if not data.get("password"):
            return (False, "Please supply a password.")
        if not data.get("passwordVerify"):
            return (False, "Please enter your password twice.")
        if data.get("password") != data.get("passwordVerify"):
            return (False, "Passwords do not match.")
        return (True, data)

    @jsonencode
    def join(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            return error("You are logged in. You cannot create an account")

        theData = json.loads(helper.getRequestBody())

        valid, msg = self.isValid(theData)
        result = None
        if valid:
            theData["password"] = hash(theData["password"])
            del theData["passwordVerify"]
            id = user.create(theData)
            theUser = user.getById(id)
            helper.setLoggedInUser(theUser)
            return data(theUser)
        else:
            return error(msg)

    @jsonencode
    def read(self, userName):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and (loggedInUser.get("userName") == userName):
            return data(user.get(userName).copy())
        else:
            return data(user.getFull(userName).copy())

    @jsonencode
    def update(self, userName):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser['userName'] == userName:
            shift.update(helper.getRequestBody())
            return ack
        else:
            return error("Operation not permitted. You don't have permission to update this account.")

    @jsonencode
    def delete(self, userName):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser['userName'] == userName:
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
            theUser = user.getFull(userName)

            if theUser and (theUser['password'] == hash(password)):
                helper.setLoggedInUser(theUser)
                return data(theUser)
            else:
                return error("Incorrect password.")
        else:
            return error("Already logged in.")

    @jsonencode
    def logout(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            helper.setLoggedInUser(None)
            return ack
        else:
            return error("No user logged in.")

    @jsonencode
    def resetPassword(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            # TODO: generate random 8 character password update user and email
            return ack
        else:
            return error("No user logged in.")


# Shift
# ==============================================================================

class Shift:
    @jsonencode
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            data = json.loads(helper.getRequestBody())
            data['createdBy'] = loggedInUser.get("_id")
            return data(shift.create(data))
        else:
            return error("Operation not permitted. You are not logged in")

    @jsonencode
    def read(self, id):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser and shift.userCanReadShift(loggedInUser.get("_id"), id):
            return data(shift.get(id))
        else:
            return error("Operation not permitted. You don't have permission to view this shift.")

    @jsonencode
    def update(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['createdBy']:
            shift.update(helper.getRequestBody())
            return ack
        else:
            return error("Operation not permitted. You don't have permission to update this shift.")

    @jsonencode
    def delete(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['createdBy']:
            shift.delete(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to delete this shift.")

    @jsonencode
    def publish(self, id):
        loggedInUser = helper.getLoggedInUser()
        publishData = json.loads(helper.getRequestBody())
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['createdBy']:
            shift.publish(id, publishData)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.")

    @jsonencode
    def unpublish(self, id):
        loggedInUser = helper.getLoggedInUser()
        theShift = shift.get(id)
        if loggedInUser and loggedInUser['_id'] == theShift['createdBy']:
            shift.unpublish(id)
            return ack
        else:
            return error("Operation not permitted. You don't have permission to publish this shift.")

# Event
# ==============================================================================

class Event:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass

# Stream
# ==============================================================================

class Stream:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass

# Permission
# ==============================================================================

class Permission:
    def create(self):
        pass
    def read(self, id):
        pass
    def update(self, id):
        pass
    def delete(self, id):
        pass

# Aggregates
# ==============================================================================

class Shifts:
    @jsonencode
    def read(self, userName):
        return data(shift.byUserName(userName))


class Groups:
    @jsonencode
    def read(self, id):
        # return only public groups
        return data(groups.inGroup(int(id)))


# Main
# ==============================================================================

class Root:
    def read(self):
        return "ShiftSpace Server 1.0"


def initRoutes():
    root = Root()
    user = User()
    shift = Shift()
    shifts = Shifts()
    group = Groups()

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

    # Shift Routes
    d.connect(name="shiftCreate", route="shift", controller=shift, action="create",
              conditions=dict(method="POST"))
    d.connect(name="shiftRead", route="shift/:id", controller=shift, action="read",
              conditions=dict(method="GET"))
    d.connect(name="shiftUpdate", route="shift/:id", controller=shift, action="update",
              conditions=dict(method="PUT"))
    d.connect(name="shiftDelete", route="shift/:id", controller=shift, action="delete",
              conditions=dict(method="DELETE"))
    d.connect(name="shiftsPublish", route="publish/:id", controller=shifts, action="publish",
              conditions=dict(method="POST"))
    d.connect(name="shiftsUnpublish", route="unpublish/:id", controller=shifts, action="unpublish",
              conditions=dict(method="POST"))
    d.connect(name="shiftsRead", route="shifts/:userName", controller=shifts, action="read",
              conditions=dict(method="GET"))

    # Group Routes
    d.connect(name="groupRead", route="group/:id", controller=group, action="read",
              conditions=dict(method="GET"))

    # Stream Routes

    # Event Routes

    return d


appconf = {'/': {'tools.proxy.on':True,
                 'request.dispatch': initRoutes(),
                 'tools.sessions.on': True,
                 'tools.sessions.storage_type': "file",
                 'tools.sessions.storage_path':"/Users/davidnolen/Sites/shiftserver/sessions",
                 'tools.sessions.timeout': 60}}

cherrypy.config.update({'server.socket_port':8080})
# TODO: The following value should be read from an environment file - David 7/4/09
app = cherrypy.tree.mount(root=None, script_name='/~davidnolen/shiftspace/shiftserver', config=appconf)
cherrypy.quickstart(app)
