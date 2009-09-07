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


class EventController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
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
            data = helper.getRequestBody()
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

    @jsonencode
    @exists
    @eventType
    @loggedin
    def markRead(self, id):
        loggedInUser = helper.getLoggedInUser()
        if event.canUpdate(id, loggedInUser["_id"]):
            return data(event.markRead(id))
        else:
            return error("Operation not permitted. You don't have permission to mark this event as read.", PermissionError)

    @jsonencode
    @exists
    @eventType
    @loggedin
    def markUnread(self, id):
        loggedInUser = helper.getLoggedInUser()
        if event.canUpdate(id, loggedInUser["_id"]):
            return data(event.markUnread(id))
        else:
            return error("Operation not permitted. You don't have permission to mark this event as unread.", PermissionError)

