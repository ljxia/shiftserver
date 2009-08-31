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


class PermissionController(ResourceController):
    @jsonencode
    @loggedin
    def create(self):
        loggedInUser = helper.getLoggedInUser()
        jsonData = helper.getRequestBody()
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
            data = helper.getRequestBody()
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
