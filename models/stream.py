import core
import utils
import schema

import user
import shift
import event
import permission

class StreamError(Exception): pass
class MissingCreatorError(StreamError): pass

# ==============================================================================
# CRUD
# ==============================================================================

def create(data, add=True):
  """
  Create a stream. Will fail if:
  1. createdBy field missing.
  """
  db = core.connect()

  data["created"] = utils.utctime()
  newStream = schema.stream()
  newStream.update(data)
  userId = newStream["createdBy"]

  if not userId:
    raise MissingCreatorError
  
  newStream["type"] = "stream"
  id = db.create(newStream)
  if add:
    user.addStream(userId, id)
  
  return id


def read(id):
  """
  Read a stream
  """
  db = core.connect()
  return db[id]


def update(data):
  """
  Update a stream.
  """
  core.update(data)


def delete(id):
  """
  Delete a stream.
  """
  db = core.connect()

  permIds = [perm["_id"] for perm in permission.permissionsForStream(id)]
  [permission.delete(permId) for permId in permIds]

  del db[id]


# ==============================================================================
# Validation
# ==============================================================================

def canCreate(id, userId):
  if user.isAdmin(userId):
    return True
  return True


def canRead(id, userId):
  """
  Returns true if:
  1. User is admin.
  2. The stream is public.
  3. The user created the stream.
  4. The user has read permission for the stream.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  if not theStream["private"]:
    return True
  readableStreams = permission.readableStreams(userId)
  return (id in readableStreams)


def canUpdate(id, userId):
  """
  Returns true if:
  1. User is admin.
  2. User created the stream.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  return False


def canDelete(id, userId):
  """
  Returns true if:
  1. User is admin.
  2. User created the stream.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  return False


def canSubscribe(id, userId):
  """
  Return true if:
  1. User is admin.
  2. User created the stream.
  3. The stream is public.
  4. User has join permissions.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  if not theStream["private"]:
    return True
  joinable = permission.joinableStreams(userId)
  return id in joinable


def canPost(id, userId):
  """
  Return true if:
  1. User is admin.
  2. User created the stream.
  3. User can write to the stream.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  writeable = permission.writeableStreams(userId)
  return id in writeable


def canAdmin(id, userId):
  """
  Return true if:
  1. User is admin.
  2. User created the stream.
  3. User can admin the stream.
  """
  if user.isAdmin(userId):
    return True
  theStream = read(id)
  if theStream["createdBy"] == userId:
    return True
  adminable = permission.adminStreams(userId)
  return id in adminable


def isOwner(id, userId):
  db = core.connect()
  return db[id]["createdBy"] == userId


def isPublic(id):
  """
  Checks if the stream is public.
  """
  db = core.connect()
  return not db[id]["private"]


def isPublicUserStream(id):
  """
  Check if the stream is a user's public stream.
  """
  db = core.connect()
  return (not db[id]["meta"] == "public")


# ==============================================================================
# Subscribe/Unsubscribe/Invite
# ==============================================================================

def subscribe(id, userId, tag=None):
  """
  Subscribe a user to a stream.
  """
  db = core.connect()
  theUser = db[userId]
  
  theStream = db[id]

  allowed = not theStream["private"]

  if not allowed:
    perms = permission.joinableStreams(userId);
    allowed = id in perms
      
  if allowed and (not id in theUser["streams"]):
    theUser["streams"].append(id)
    db[userId] = theUser
    if theStream["private"]:
      perm = permission.permissionForUser(userId, id)
      permission.update(perm["_id"], 1)


def unsubscribe(id, userId):
  """
  Unsubscribe a user to a stream.
  """
  db = core.connect()
  theUser = db[userId]
  
  if id in theUser["streams"]:
    theUser["streams"].remove(id)
    db[userId] = theUser


def invite(id, adminId, userId):
  """
  Give a user join permission.
  """
  db = core.connect();

  permission.create({
      "streamId": id,
      "createdBy": adminId,
      "userId": userId,
      "level": 0
      })

  event.create({
      "createdBy": userId,
      "streamId": user.messageStream(userId),
      "displayString": "%s has invited you to the %s %s" % (user.nameForId(adminId), meta(id), displayName(id)),
      "unread": True
      })


# ==============================================================================
# Utilities
# ==============================================================================


def displayName(id):
  db = core.connect()
  return db[id]["displayName"]


def meta(id):
  db = core.connect()
  return db[id]["meta"]  


def subscribers(id):
  return core.query(schema.streamBySubscribers, id)


def streamsForObjectRef(objectRef):
  """
  All streams for a objectRef, where objectRef is "type:id".
  """
  return core.query(schema.streamByObjectRef, objectRef)


def streamsByCreator(userId):
  """
  All streams created by a particular user
  """
  return core.query(schema.streamByCreator, userId)


def byUniqueName(uniqueName):
  """
  Return the stream with a unique name.
  """
  return core.single(schema.streamByUniqueName, uniqueName)


def notifications(id):
  """
  Return a list of all users who should be notified of an event on a stream.
  """
  return core.query(schema.notify, id)
