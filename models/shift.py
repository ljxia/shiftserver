import utils
import core
import schema

import user
import stream
import event
import permission

def ShiftError(Exception): pass
def ShiftSchemaConflictError(ShiftError): pass

def ref(id):
  return "shift:"+id

# ==============================================================================
# CRUD
# ==============================================================================

def create(data):
  """
  Create a shift in the database.
  """
  db = core.connect()

  theTime = utils.utctime()
  data["created"] = theTime
  data["modified"] = theTime

  newShift = schema.shift()
  newShift.update(data)
  newShift["type"] = "shift"
  return db.create(newShift)


def read(id):
  """
  Get a specific shift.
  """
  db = core.connect()
  return db[id]


def update(id, data):
  """
  Update a shift in the database.
  """
  db = core.connect()

  theShift = db[id]
  theShift.update(data)
  print theShift
  theShift["modified"] = utils.utctime()

  db[id] = theShift
  return theShift


def delete(id):
  """
  Delete a shift from the database.
  """
  db = core.connect()
  # FIXME: What happens to orphaned comments? - David 7/6/09
  del db[id]


# ==============================================================================
# Validation
# ==============================================================================

def canRead(shiftId, userId):
  """
  Check if a user can read a shift. The user must have
  either:
  
  1. Created the shift
  2. The shift must be published and public
  3. If the user is subscribed to a stream the shift is on.
  4. If the shift is published to the user's private stream.
  """
  db = core.connect()

  theShift = db[shiftId]

  if user.isAdmin(userId):
    return True

  if theShift["createdBy"] == userId:
    return True

  if theShift["publishData"]["draft"]:
    return False

  theUser = db[userId]

  if not theShift["publishData"]["private"]:
    return True

  if theUser["privateStream"] in theShift["publishData"]["streams"]:
    return True

  shiftStreams = theShift["publishData"]["streams"]
  readableStreams = permission.readableStreams(userId)

  allowed = set(shiftStreams).intersection(readableStreams)

  return len(allowed) > 0


def canUpdate(shiftId, userId):
  db = core.connect()
  theShift = db[shiftId]
  return user.isAdmin(userId) or (userId == theShift['createdBy'])


def canDelete(shiftId, userId):
  db = core.connect()
  theShift = db[shiftId]
  return user.isAdmin(userId) or (userId == theShift['createdBy'])


def canPublish(shiftId, userId):
  db = core.connect()
  theShift = db[shiftId]
  return user.isAdmin(userId) or (userId == theShift['createdBy'])


def canUnpublish(shiftId, userId):
  db = core.connect()
  theShift = db[shiftId]
  return user.isAdmin(userId) or (userId == theShift['createdBy'])


def canComment(id, userId):
  """
  Check if the user can comment on a shift. Allowed if:

  1. Shift is public.
  2. If the shift was published to a stream that the user has permissions on.
  """
  db = core.connect()
  theShift = db[id]

  if not theShift["publishData"]["private"]:
    return True

  # ignore private streams
  shiftStreams = [astream for astream in theShift["publishData"]["streams"]
                  if not stream.isUserPrivateStream(astream)]
  
  writeable = permission.writeableStreams(userId)
  allowed = set(shiftStreams).intersection(writeable)
  return len(allowed) > 0


def isPublic(id):
  db = core.connect()
  theShift = db[id]
  publishData = theShift["publishData"]
  return (not publishData["draft"]) and (not publishData["private"])


def isPrivate(id):
  db = core.connect()
  theShift = db[id]
  publishData = theShift["publishData"]
  return publishData["private"]


# ==============================================================================
# Publishing
# ==============================================================================

def publish(id, publishData):
  """
  Set draft status of a shift to false. Sync publishData field.
  If the shift is private only publish to the streams that
  the user has access. If the shift is publich publish it to
  any of the public non-user streams. Creates the comment stream
  if it doesn't already exist.
  """
  db = core.connect()

  theShift = db[id]
  theUser = db[theShift["createdBy"]]
  userId = theUser["_id"]

  allowed = []
  publishStreams = publishData.get("streams") or []

  if (publishData.get("private") == True) or (publishData.get("private") == None and isPrivate(id)):
    allowedStreams = permission.writeableStreams(userId)
    allowed = list(set(allowedStreams).intersection(set(publishStreams)))
    # add any private user streams this shift is directed to
    if publishData.get("users"):
      allowed.extend([user.privateStream(user.idForName(userName)) 
                      for userName in publishData["users"]
                      if user.read(userName)])
      del publishData["users"]
    # add streams this user can post to
    allowed.extend([astream for astream in publishStreams
                    if stream.canPost(astream, userId)])
  else:
    allowed.append(user.publicStream(userId))

  # TODO: commentStreams should use the permission of the streams the shift has been published to. -David 7/14/09
  if not commentStream(id):
    createCommentStream(id)

  # remove duplicates
  publishData["streams"] = list(set(allowed))
  
  newData = theShift["publishData"]
  newData.update(publishData)
  theShift["publishData"] = newData
  theShift["publishData"]["draft"] = False

  db[id] = theShift


def unpublish(id):
  """
  Set the draft status of a shift back to True"
  """
  db = core.connect()

  theShift = db[id]
  theShift["publishData"]["draft"] = True

  db[id] = theShift


# ==============================================================================
# Comments
# ==============================================================================

def commentStream(id):
  stream = core.single(schema.commentStreams, id)
  if stream:
    return stream["_id"]
  else:
    return None


def createCommentStream(id):
  db = core.connect()

  theShift = db[id]
  stream.create({
      "meta": "comments",
      "objectRef": ref(id),
      "createdBy": theShift["createdBy"]
      })


# ==============================================================================
# Utilities
# ==============================================================================

def byUser(userId):
  return core.query(schema.shiftByUser, userId)


def byUserName(userName):
  """
  Return the list of shifts a user has created.
  """
  userId = user.idForName(userName)
  return byUser(schema.shiftByUser, userId)
