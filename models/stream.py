import core
import utils
import schema


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
  if user.isAdmin(userId):
    return True

  theStream = read(id)
  if theStream["public"]:
    return True

  readableStreams = permissions.readableStreams(userId)
  return (id in readableStreams)


def canUpdate(id, userId):
  pass


def canDelete(id, userId):
  pass


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
