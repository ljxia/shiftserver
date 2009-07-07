import utils
import core
import schema

import user
import stream
import event
import permission


def ref(id):
  return "shift:"+id


def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  theTime = utils.utctime()
  data["created"] = theTime

  newShift = schema.shift()
  newShift.update(data)
  
  shiftId = db.create(newShift)
  newShift = db[shiftId]

  # update shift with stream data
  streamId = stream.create({
      "objectRef":ref(shiftId),
      "createdBy":newShift["createdBy"],
      "created":theTime,
      "private":newShift["publishData"]["private"]
  })
  
  shiftStream = db[streamId]
  newShift['streams'] = [streamId]

  db[shiftId] = newShift

  return shiftId


def get(id):
  """
  Get a specific shift.
  """
  db = core.connect()
  return db[id]


def delete(id):
  """
  Delete a shift from the database.
  """
  db = core.connect()
  # FIXME: What happens to orphaned comments? - David 7/6/09
  del db[id]


def update(data):
  """
  Update a shift in the database.
  """
  db = core.connect()

  id = data["id"]
  doc = db[id]
  doc.update(data)
  doc["modified"] = utils.utctime()

  db[id] = doc

  return doc


def byUserName(userName):
  """
  Return the list of shifts a user has created.
  """
  userId = user.idForName(userName)
  return core.query("_design/shifts/_view/byuser", userId)


def userCanReadShift(userId, shiftId):
  """
  Check if a user can read a shift. The user must have
  either:
  
  1. Created the shift
  2. The shift must be published and public
  3. The shift is private and the user has read permissions
     for a stream containing the shift.
  """
  db = core.connect()

  theShift = db[shiftId]

  if theShift["createdBy"] == userId:
    return True

  if theShift["publishData"]["draft"]:
    return False

  theUser = db[userId]

  if not theShift["publishData"]["private"]:
    return True

  streams = stream.streamsForObjectRef(ref(shiftId))
  streamIds = [astream["_id"] for astream in streams]

  perms = permission.permissionsForUser(userId)
  permStreamIds = [aperm["streamId"] for aperm in perms if aperm["level"] >= 1]

  allowed = set(streamIds).intersection(set(permStreamIds))

  if len(allowed) > 0:
    return True


def publish(data):
  db = core.connect()

  if not data.get("publishData").get("private"):
    # public, publish to followers
    streamId = user.publicStream(data.get("createdBy")).get("_id")
    publishToSubscribers(data, stream.subscribers(streamId))
  else:
    # publish to specified streams
    streamIds = date.get("publishData").get("streams")
    streams = [db[streamId] for streamId in streamIds]
    
    for stream in streams:
      publishToSubscribers(data, stream.get("subscribers"))


def publishToSubscribers(data, subscribers):
  for subscriber in subscribers:
    userStream = stream.forUniqueName(user.ref(subscriber)+":public")

    event.create({
        "streamId": userStream["_id"],
        "createdBy": data["createdBy"],
        "subscriber": subscriber,
        "objectRef": ref(data["_id"]),
        "created": data["created"],
        "displayString": data["summary"]
        })


def unpublish(id):
  pass
