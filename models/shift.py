import utils
import core
import user
import stream
import schema
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


def publish(publishData):
  db = core.connect()

  if not publishData.get("private"):
    # publish to public streams
    pass
  else:
    # publish to specified streams
    streamIds = publishData["streams"]
    streams = [db[streamId] for streamId in streamIds]
    
    for stream in streams:
      subscribers = stream.get("subscribers")
      if len(subcribers) > 0:
        for subscriber in subscribers:
          userStream = stream.forUniqueName(user.ref(subscriber)+":public")
          event.create({
              "streamId": userStream["_id"]
            
              })
      else:
        pass


def unpublish(id):
  pass
