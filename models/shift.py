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
  3. If the user is subscribed to a stream the shift is on.
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

  shiftStreams = theShift["publishData"]["streams"]
  readableStreams = permissions.readableStreams(userId)

  allowed = set(shiftStreams).intersection(set(readableStreams))

  if len(allowed) > 0:
    return True


def publish(id, publishData):
  """
  Set draft status of a shift to false. Sync publishData field.
  """
  db = core.connect()

  theShift = db[id]
  theUser = db[theShift["createdBy"]]
  userId = theUser["_id"]

  allowed = []
  publishStreams = publishData["streams"]

  # if private shift check against the streams the user can write to
  if publishData["private"]:
    allowedStreams = permission.writeableStreams(userId)
    allowed = list(set(allowedStreams).intersection(set(publishStreams)))
  else:
    # publish to the users public stream - used when following
    allowed = allowed.append(user.publicStream(userId)["_id"])

  # also include any public streams if specified
  publicStreams = [astream for astream in publishStreams if stream.isPublic(astream)]
  allowed.extend(publicStreams)
    
  publishData["streams"] = allowed
  theShift["publishData"] = publishData
  theShift["publishData"]["draft"] = False

  db[shiftId] = theShift


def unpublish(id):
  """
  Set the draft status of a shift back to True"
  """
  db = core.connect()

  theShift = db[id]
  theShift["publishData"]["draft"] = True

  db[id] = theShift
