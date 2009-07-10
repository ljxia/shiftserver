import core
import utils
import schema

import user

# ==============================================================================
# CRUD
# ==============================================================================

def create(data):
  """
  Create a stream.
  """
  db = core.connect()

  data["created"] = utils.utctime()

  newStream = schema.stream()
  newStream.update(data)

  return db.create(newStream)


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
  pass


def delete(id):
  """
  Delete a stream.
  """
  pass


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
  readableStreams = permissions.readableStreams(userId)
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


def isPublic(id):
  db = core.connect()
  return not db[id]["private"]


def isPublicUserStream(id):
  db = core.connect()
  return (not db[id]["meta"] == "userPublicStream")


# ==============================================================================
# Subscribe/Unsubscribe
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
    perms = permission.readableStreams(userId);
    allowed = id in perms
      
  if allowed:
    theUser["streams"].append(id)
    db[userId] = theUser


def unsubscribe(id, userId):
  """
  Unsubscribe a user to a stream.
  """
  db = core.connect()
  theUser = db[userId]
  
  if id in theUser["streams"]:
    theUser["streams"].remove(id)
    db[userId] = theUser


# ==============================================================================
# Utilities
# ==============================================================================

def subscribers(streamId):
  return core.query(schema.streamBySubscribers, streamId)


def streamsForObjectRef(objectRef):
  """
  All streams for a objectRef, where objectRef is "type:id".
  """
  return core.query(schema.streamByObjectRef, objectRef)


def byUniqueName(uniqueName):
  """
  Return the stream with a unique name.
  """
  return core.single(schema.streamByUniqueName, uniqueName)
