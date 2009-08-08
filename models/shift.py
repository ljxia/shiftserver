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


def byHref(href):
  """
  Return the list of shifts at a particular url.
  """
  shifts = core.query(schema.shiftByHref, href)
  for shift in shifts:
    shift["gravatar"] = user.readById(shift["createdBy"])["gravatar"]
  return shifts


def shifts(byHref, userId=None, byFollowing=False, byGroups=False, start=0, perPage=25):
  """
  Returns a list of shifts based on whether
  1. href
  3. By public streams specified user is following. 
  4. By groups streams specified user is following.
  
  Parameters:
  byHref - a url
  byDomain - a url string
  byFollowing - a user id
  byGroups - a user id
  """
  db = core.connect()
  lucene = core.lucene()
  # TODO: validate byHref - David
  queryString = "(href:%s AND draft:false AND private:false)" % byHref
  if userId:
    streams = ""
    if byFollowing:
      following = user.followStreams(userId)
      streams = streams + " ".join(following)
    if byGroups:
      groups = user.groupStreams(userId)
      streams = streams + " ".join(groups)
    # TODO: make sure streams cannot be manipulated from client - David
    queryString = queryString + (" OR (draft:false AND streams:%s)" % streams)
  print queryString
  rows = lucene.search("shifts", q=queryString, sort="\modified", skip=start, limit=perPage)
  return [db[row["id"]] for row in rows]
