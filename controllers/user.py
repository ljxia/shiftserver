from utils.utils import *
from utils.errors import *
from utils.decorators import *
from utils.returnTypes import *
from models import user
from models import shift
from models import stream
from models import event
from models import permission
from resource import *


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
            theData["gravatar"] = "http://www.gravatar.com/avatar/%s?s=32" % md5hash(theData["email"])
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
    @exists
    @loggedin
    def follow(self, userName):
        loggedInUser = helper.getLoggedInUser()
        follower = loggedInUser["_id"]
        followed = user.idForName(userName)
        if follower == followed:
            return error("You cannot follow yourself.", FollowError)
        else:
            user.follow(follower, followed)
            return ack

    @jsonencode
    @exists
    @loggedin
    def unfollow(self, userName):
        loggedInUser = helper.getLoggedInUser()
        follower = loggedInUser["_id"]
        followed = user.idForName(userName)
        if follower == followed:
            return error("You cannot unfollow yourself.", FollowError)
        else:
            user.unfollow(follower, followed)
            return ack

    @jsonencode
    @exists
    @loggedin
    def messages(self, userName):
        loggedInUser = helper.getLoggedInUser()
        messageStream = user.messageStream(user.idForName(userName))
        if stream.canRead(messageStream, loggedInUser["_id"]):
            return data(event.eventsForStream(messageStream))
        else:
            return error("You do not have permission to view this user's messages.", PermissionError)

    @jsonencode
    @exists
    @loggedin
    def feeds(self, userName):
        loggedInUser = helper.getLoggedInUser()
        userId = loggedInUser["_id"]
        if user.isAdmin(userId) or user.idForName(userName) == userId:
            return data(user.feeds(userId))
        else:
            return error("You don't have permission to view this feed.", PermissionError)

    @jsonencode
    @exists
    @loggedin
    def shifts(self, userName):
        loggedInUser = helper.getLoggedInUser()
        userId = loggedInUser["_id"]
        if user.isAdmin(userId) or user.idForName(userName) == userId:
            return data(shift.byUserName(userName))
        else:
            return error("You don't have permission to view this user's shifts.", PermissionError)
