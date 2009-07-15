import utils
import core
import schema

import user
import stream
import event
import permission


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


def update(data):
  """
  Update a shift in the database.
  """
  db = core.connect()

  id = data["id"]
  doc = db[id]
  doc.update(data)
  doc["modified"] = utils.utctime()

  if core.validate(doc):
    db[id] = doc
    return doc
  else:
    # TODO: throw an exception - David 7/9/09
    return None


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

  shiftStreams = theShift["publishData"]["streams"]
  readableStreams = permissions.readableStreams(userId)

  allowed = set(shiftStreams).intersection(set(readableStreams))

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
  db = core.connect()
  theShift = db[id]

  if not theShift["publishData"]["private"]:
    return True
  else:
    shiftStreams = theShift["publishData"]["streams"]
    userStreams = permission.writeableStreams(userId)
    
    allowed = set(shiftStreams).intersection(userStreams)
    
    return len(allowed) > 0


def isPublic(id):
  db = core.connect()
  theShift = db[id]
  publishData = theShift["publishData"]
  return (not publishData["draft"]) and (not publishData["private"])


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

  # if private shift check against the streams the user can write to
  if publishData["private"]:
    allowedStreams = permission.writeableStreams(userId)
    allowed = list(set(allowedStreams).intersection(set(publishStreams)))
  else:
    # publish to the users public stream - used when following
    allowed.append(user.publicStream(userId))
    # also include any public streams if specified, excluding
    # the public streams of other users
    publicStreams = [astream for astream in publishStreams
                     if stream.isPublic(astream) and (not stream.isUserPublicStream(astream))]
    allowed.extend(publicStreams)
    if not commentStream(id):
      createCommentStream(id)

  # TODO: publish to user's private stream for @user - David
    
  publishData["streams"] = allowed
  theShift["publishData"] = publishData
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
  return core.single(schema.commentStreams, id)


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
