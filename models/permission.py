import core
import utils
import schema

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
  

