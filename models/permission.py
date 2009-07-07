import core
import utils

def permissionsForUser(userId):
  """
  Returns all permission documents for a particular user.
  """
  db = core.connect()
  return core.query("_design/permissions/_view/byuser", userId)


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
  

