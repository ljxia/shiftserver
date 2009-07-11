import core
import schema

import user
import shift
import stream
import event
import permission


def deleteAllShifts():
  shiftIds = [ashift["_id"] for ashift in core.query(schema.allShifts)]
  [permission.delete(shiftId) for shiftId in shiftIds]


def deleteAllUsers():
  pass


def deleteAllPermissions():
  permIds = [aperm["_id"] for aperm in core.query(schema.allPermissions)]
  [permission.delete(permId) for permId in permIds]


def deleteAllStreams():
  streamIds = [astream["_id"] for astream in core.query(schema.allStreams)]
  [stream.delete(streamId) for streamId in streamIds]
