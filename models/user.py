import core
import utils
import schema

import shift
import stream
import event

ref = utils.genrefn("user")

# ==============================================================================
# CRUD
# ==============================================================================

def create(data):
  """
  Create a new user.
  """
  db = core.connect()

  data["joined"] = utils.utctime()

  newUser = schema.user()
  newUser.update(data)

  newUser["type"] = "user"
  userId = db.create(newUser)

  userRef = ref(userId)

  # create public stream for user
  # for when the user publishes her/his own content
  publicStream = stream.create({
      "objectRef": userRef, 
      "uniqueName": ref(userId,"public"),
      "private": False,
      "meta": "userPublicStream",
      "createdBy": userId
      }, False)

  # create the message stream for the user
  messageStream = stream.create({
      "objectRef": userRef, 
      "uniqueName": ref(userId, "messages"), 
      "private": True, 
      "meta": "userMessageStream",
      "createdBy": userId
      }, False)

  theUser = db[userId]
  theUser.update({
      "messageStream": messageStream,
      "publicStream": publicStream
      })
  
  db[userId] = theUser

  return userId


def read(userName):
  """
  Returns public data for a user.
  """
  theUser = readFull(userName)
  
  if theUser:
    del theUser["email"]
    del theUser["streams"]
    del theUser["password"]
  
  return theUser


def readFull(userName, deleteType=True):
  """
  Return the full data for a user.
  """
  theUser = core.single(schema.userByName, userName)

  if theUser and deleteType:
    del theUser["type"]

  return theUser


def readById(id):
  """
  Return the user by id.
  """
  db = core.connect()
  return db[id]


def update(data):
  """
  Update a user document.
  """
  data["modified"] = utils.utctime()
  return core.update(data)


def delete(userName):
  """
  Delete a user.
  """
  db = core.connect()
  id = idForName(userName)

  # delete the user's events
  userEvents = [anevent["_id"] for anevent in event.eventsForUser(id)]
  for eventId in userEvents:
    del db[eventId]

  # delete the user's public and message streams
  userStreams = [astream["_id"] for astream in stream.streamsForObjectRef(ref(id))]
  for streamId in userStreams:
    del db[streamId]

  # delete all of the remaining user's streams which have no events
  streamIds = utils.ids(stream.streamsByCreator(id))
  [stream.delete(streamId) for streamId in streamIds
   if len(event.eventsForStream(streamId)) == 0]

  # delete the user's shifts
  userShifts = [ashift["_id"] for ashift in shift.byUser(id)]
  for shiftId in userShifts:
    del db[shiftId]

  # delete the user
  del db[id]

# ==============================================================================
# Validation
# ==============================================================================

def canReadFull(id, userId):
  return (id == userId) or isAdmin(userId)


def canUpdate(id, userId):
  return (id == userId) or isAdmin(userId)


def canDelete(id, userId):
  return (id == userId) or isAdmin(userId)


def isAdmin(id):
  """
  Return true if the user is in the admin list.
  """
  db = core.connect()
  admins = db["admins"]
  return id in admins["ids"]


def nameIsUnique(userName):
  """
  Returns True or False depending on if the name is taken.
  """
  # FIXME: cannot protect unless it's the document id - David Nolen 7/6/09
  return read(userName) == None


# ==============================================================================
# Streams
# ==============================================================================

def publicStream(id):
  return readFull(nameForId(id))["publicStream"]


def messageStream(id):
  return readFull(nameForId(id))["messageStream"]


def follow(follower, followed):
  """
  Subscribe a user to another user's public stream. A user's public
  stream is only for shifts at the moment. Both arguments should
  be the userNames.
  """
  stream.subscribe(publicStream(followed).get("_id"), idForName(follower))


def unfollow(follower, followed):
  """
  Unsubscribe a user from another user's public stream. Both arguments
  should be userNames.
  """
  stream.unsubscribe(publicStream(followed).get("_id"), idForName(follower))


def feeds(id, page=0, perPage=25):
  """
  Return all events for all streams that a user is subscribed to.
  """
  db = core.connect()
  theUser = db[id]
  streams = theUser["streams"]
  pass


def feed(id, streamId):
  """
  Return all events for a single feed.
  """
  pass

# ==============================================================================
# Utilties
# ==============================================================================

def getById(id):
  """
  Get a user by document id.
  """
  db = core.connect()
  return db[id]


def idForName(userName):
  """
  Get the id for a user from the userName.
  """
  theUser = readFull(userName)
  if theUser:
    return theUser["_id"]


def nameForId(id):
  db = core.connect()
  return db[id]["userName"]


def updateLastSeen(userName):
  db = core.connect()
  theUser = readFull(userName, False)
  theUser["lastSeen"] = utils.utctime()
  db[theUser["_id"]] = theUser


def addStream(id, streamId):
  db = core.connect()
  theUser = db[id]
  if stream.canSubscribe(streamId, id) and (not streamId in theUser["streams"]):
    theUser["streams"].append(streamId)
    db[id] = theUser


def isSubscribed(id, streamId):
  db = core.connect()
  theUser = db[id]
  return streamId in theUser["streams"]

