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


class ShiftController(ResourceController):
    @jsonencode
    def shifts(self, byHref, byDomain=None, byFollowing=False, byGroups=False):
        loggedInUser = helper.getLoggedInUser()
        if loggedInUser:
            return data(shift.shifts(byHref, 
                                     userId=loggedInUser.get("_id"), 
                                     byFollowing=byFollowing, 
                                     byGroups=byGroups))
        else:
            return data(shift.shifts(byHref, None, byFollowing, byGroups))

    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            id = loggedInUser.get("_id")
            theData['createdBy'] = id
            theData['userName'] = user.nameForId(id)
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
        jsonData = helper.getRequestBody()
        if jsonData != "":
            shiftData = json.loads(jsonData)
            if shift.canUpdate(id, loggedInUser['_id']):
                return data(shift.update(id, shiftData))
            else:
                return error("Operation not permitted. You don't have permission to update this shift.", PermissionError)
        else:
            return error("No data for shift.", NoDataError)

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
        # NOTE: should mabye take publishData url parameter - David 9/5/2009
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
    @exists
    @shiftType
    def favorite(self, id):
        loggedInUser = helper.getLoggedInUser()
        loggedInId = loggedInUser["_id"]
        if shift.isPublic(id) or (shift.canRead(id, loggedInId)):
            return data(shift.favorite(id, userId))
        else:
            return error("Operation not permitted. You don't have permission to favorite this shift.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    def unfavorite(self, id):
        loggedInUser = helper.getLoggedInUser()
        loggedInId = loggedInUser["_id"]
        if shift.isPublic(id) or (shift.canRead(id, loggedInId)):
            return data(shift.unfavorite(id, userId))
        else:
            return error("Operation not permitted. You don't have permission to unfavorite this shift.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    def comments(self, id):
        loggedInUser = helper.getLoggedInUser()
        if shift.isPublic(id) or (shift.canRead(id, loggedInUser["_id"])):
            return data(event.eventsForStream(shift.commentStream(id)))
        else:
            return error("Operation not permitted. You don't have permission to view comments on this shift.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def comment(self, id):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
        if jsonData != "":
            theData = json.loads(jsonData)
            if shift.canComment(id, loggedInUser["_id"]):
                theUser = user.readById(loggedInUser["_id"])
                theShift = shift.read(id)
                event.create({
                        "meta": "comment",
                        "objectRef": "shift:%s" % id,
                        "streamId": shift.commentStream(id),
                        "displayString": "%s just commented on your %s on %s" % (theUser["userName"], theShift["space"]["name"], theShift["href"]),
                        "createdBy": loggedInUser["_id"],
                        "content": {"text":theData["text"]}
                        })
                return ack
            else:
                return error("Operation not permitted. You don't have permission to comment on this shift.", PermissionError)
        else:
            return error("No data for comment.", NoDataError)

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def notify(self, id):
        loggedInUser = helper.getLoggedInUser()
        userId = loggedInUser["_id"]
        if shift.canRead(id, userId):
            if (not shift.commentStream(id) in user.readById(userId)["notify"]):
                user.addNotification(userId, shift.commentStream(id))
                return ack
            else:
                return error("You are already getting notification from this stream", AlreadyBeingNotifiedError)
        else:
            return error("Operation not permitted. You don't have permission to be notified of events on this stream.", PermissionError)

    @jsonencode
    @exists
    @shiftType
    @loggedin
    def unnotify(self, id):
        loggedInUser = helper.getLoggedInUser()
        userId = loggedInUser["_id"]
        if shift.commentStream(id) in user.readById(userId)["notify"]:
            user.removeNotification(userId, id)
            return ack
        else:
            return error("You are not getting notification from this stream.", NotBeingNotifiedError)
