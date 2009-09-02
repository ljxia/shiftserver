import utils.utils as utils
import core
import stream
import schema
import user
import permission

# ==============================================================================
# CRUD
# ==============================================================================

def create(data):
    db = core.connect()
    theTime = utils.utctime()
    data["created"] = theTime
    # create notification events
    notifications = stream.notifications(data["streamId"])
    for userId in notifications:
        create({
                "createdBy": data.get("createdBy"),
                "displayString": data.get("displayString"),
                "streamId": user.messageStream(userId),
                "unread": True,
                "content": data.get("content")
                })
    newEvent = schema.event()
    newEvent.update(data)
    newEvent["type"] = "event"
    return db.create(newEvent)

def read(id):
    db = core.connect()
    return db[id]

def update(data):
    db = core.connect()
    id = data["id"]
    doc = db[id]
    doc.update(data)
    doc["modified"] = utils.utctime()
    if core.validate(doc):
        db[id] = doc
        return db[id]
    else:
        # TODO: throw an exception - David 7/9/09
        return None

def delete(id):
    db = core.connect()
    del db[id]

# ==============================================================================
# Validation
# ==============================================================================

def canCreate(data, userId):
    if user.isAdmin(userId):
        return True
    streamId = data["streamId"]
    theStream = stream.read(userId)
    if not theStream["private"]:
        return True
    writeable = permission.writeableStreams(userId)
    return (streamId in writeable)

def canRead(id, userId):
    if user.isAdmin(userId):
        return True
    streamId = data["streamId"]
    theStream = stream.read(userId)
    if not theStream["private"]:
        return True
    readable = permission.readableStreams(userId)
    return (streamId in readable)

def canUpdate(id, userId):
    if user.isAdmin(userId):
        return True
    theEvent = read(id)
    return theEvent["createdBy"] == userId

def canDelete(id, userId):
    if user.isAdmin(userId):
        return True
    theEvent = read(id)
    return theEvent["createdBy"] == userId

# ==============================================================================
# Utilities
# ==============================================================================

def eventsForStream(streamId):
    return core.query(schema.eventByStream, streamId)

def eventsForUser(userId):
    return core.query(schema.eventByUser, userId)

def setRead(id, value):
    pass
