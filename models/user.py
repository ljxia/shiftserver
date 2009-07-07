import core
import utils
import schema

import shift
import stream
import event


def ref(id):
  return "user:"+id


def create(data):
  """
  Create a new user.
  """
  db = core.connect()

  data["joined"] = utils.utctime()

  newUser = schema.user()
  newUser.update(data)

  userId = db.create(newUser)

  userRef = ref(userId)

  # create personal stream for user
  # for when people publish to the user's subscribed streams
  privateStream = stream.create({
      "objectRef": userRef, 
      "uniqueName": userRef+":private", 
      "private": True, 
      "createdBy": userId
      })

  # create public stream for user
  # for when the user publishes her/his own content
  publicStream = stream.create({
      "objectRef": userRef, 
      "uniqueName": userRef+":public", 
      "private": False, 
      "createdBy": userId
      })

  # create the message stream for the user
  messageStream = stream.create({
      "objectRef": userRef, 
      "uniqueName": userRef+":messages", 
      "private": False, 
      "createdBy": userId
      })

  theUser = db[userId]
  theUser.update({"streams":[privateStream, messageStream]})
  db[userId] = theUser

  return userId


def publicStream(userName):
  return core.single("_design/streams/_view/byuniquename", ref(idForName(userName))+":public")


def privateStream(userName):
  return core.single("_design/streams/_view/byuniquename", ref(idForName(userName))+":private")


def messageStream(userName):
  return core.single("_design/streams/_view/byuniquename", ref(idForName(userName))+":messages")


def get(userName):
  """
  Returns public data for a user.
  """
  theUser = getFull(userName)
  
  if theUser:
    del theUser["email"]
    del theUser["groups"]
    del theUser["following"]
    del theUser["password"]
  
  return theUser


def getFull(userName):
  """
  Return the full data for a user.
  """
  theUser = core.single("_design/users/_view/byname", userName)

  if theUser:
    del theUser["type"]

  return theUser


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
  theUser = get(userName)
  if theUser:
    return theUser["_id"]


def nameForId(id):
  db = core.connect()
  return db[id].get("userName")


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

  del db[id]

  # delete the user's private, public, and message streams
  userStreams = [astream["_id"] for astream in stream.streamsForObjectRef(ref(id))]
  for streamId in userStreams:
    del db[streamId]

  # delete the user's shifts
  userShifts = [ashift["_id"] for ashift in shift.byUserName(userName)]
  for shiftId in userShifts:
    del db[shiftId]

  # delete the user's events
  userEvents = [anevent["_id"] for anevent in event.eventsForUser(id)]
  for eventId in userEvents:
    del db[eventId]


def nameIsUnique(userName):
  """
  Returns True or False depending on if the name is taken.
  """
  return get(userName) == None


def follow(follower, followed):
  stream.subscribe(publicStream(followed), idForName(follower))


def unfollow(follower, followed):
  stream.unsubscribe(publicStream(followed), idForName(follower))


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
