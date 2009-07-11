import core
import utils
import schema

class PermissionError(Exception): pass
class CreateEventMissingCreatorError(PermissionError): pass
class CreateEventMissingStreamError(PermissionError): pass
class CreateEventOnPublicStreamError(PermissionError): pass
class CreateEventPermissionError(PermissionError): pass
class PermissionAlreadyExistsError(PermissionError): pass

# ==============================================================================
# CRUD
# ==============================================================================

def create(data):
  """
  Create will fail if:
  1. No stream specified.
  2. No creator specified.
  3. Attempting to create an event on a public stream.
  4. Attempting to create a permission for a user on a stream if a permission
     for that user on that stream already exists.
  5. Attempting to create an event without proper permission.
  """
  db = core.connect()
  streamId = data["streamId"]
  createdBy = data["createdBy"]

  if not streamId:
    raise CreateEventMissingStreamError
  if not createdBy:
    raise CreateEventMissingCreatorError
  if stream.isPublic(streamId):
    raise CreateEventOnPublicStreamError
  if permission.permissionForUser(createdBy):
    raise PermissionAlreadyExistsError
  if not user.isAdmin(createdBy):
    adminable = adminStreams(createdBy)
    if not streamId in adminable:
      raise CreateEventPermissionError
  
  return db.create(data)


def read(id):
  pass


def update(id, level):
  """
  Can only update the level after permission creation.
  """
  perm = read(id)
  


def delete(id):
  pass

# ==============================================================================
# Utilities
# ==============================================================================

def permissionForUser(userId, streamId):
  return core.single(schema.permissionByUserAndStream, [userId, streamId])


def permissionsForUser(userId):
  """
  Returns all permission documents for a particular user.
  """
  db = core.connect()
  return core.query(schema.permissionByUser, userId)


def joinableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser[userId]
          if aperm["level"] == 0]


def readableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser[userId]
          if aperm["level"] >= 1]


def writableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser[userId]
          if aperm["level"] >= 2]


def adminStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser[userId]
          if aperm["level"] >= 3]


def ownerStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser[userId]
          if aperm["level"] == 4]
  

