import core
import utils
import schema

import user
import stream
import event

class PermissionError(Exception): pass
class MissingCreatorError(PermissionError): pass
class MissingStreamError(PermissionError): pass
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
  5. Attempting to create an event without proper permission. Must either be
     an amdin for that stream or running as admin for shiftserver.
  """
  db = core.connect()
  streamId = data["streamId"]
  createdBy = data["createdBy"]

  if not streamId:
    raise MissingStreamError
  if not createdBy:
    raise MissingCreatorError
  if stream.isPublic(streamId):
    raise CreateEventOnPublicStreamError
  if permissionForUser(createdBy, streamId):
    raise PermissionAlreadyExistsError

  allowed = user.isAdmin(createdBy)

  if not allowed:
    allowed = stream.isOwner(streamId, createdBy)

  if not allowed:
    adminable = adminStreams(createdBy)
    allowed = streamId in adminable

  if not allowed:
    raise CreateEventPermissionError
  
  newPermission = schema.permission()
  newPermission.update(data)
  newPermission["type"] = "permission"

  return db.create(newPermission)


def read(id):
  return db[id]


def update(id, level):
  """
  Can only update the level after permission creation.
  """
  perm = read(id)
  perm["level"] = level
  db[id] = perm


def updateForUser(userId, streamId, level):
  perm = permissionForUser(userId, streamId)
  update(perm["_id"], level)


def delete(id):
  db = core.connect()
  del db[id]

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


def permissionsForStream(streamId):
  """
  Returns all permission documents a particular user.
  """
  db = core.connect()
  return core.query(schema.permissionByStream, streamId)


def joinableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser(userId)
          if aperm["level"] == 0]


def readableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser(userId)
          if aperm["level"] >= 1]


def writableStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser(userId)
          if aperm["level"] >= 2]


def adminStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser(userId)
          if aperm["level"] >= 3]


def ownerStreams(userId):
  return [aperm["streamId"] for aperm in permissionsForUser(userId)
          if aperm["level"] == 4]
  

