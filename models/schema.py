# ==============================================================================
# Views
# ==============================================================================

permissionByUser = "_design/permissions/_view/byuser"
permissionByUserAndStream = "_design/permissions/_view/by_user_and_stream"
streamByObjectRef = "_design/streams/_view/byobjectref"
streamByUniqueName = "_design/streams/_view/byuniquename"
streamByCreator = "_design/streams/_view/bycreator"
streamBySubscribers = "_design/streams/_view/subscribers"
userByName = "_design/users/_view/byname"
eventByStream = "_design/events/_view/bystream"
eventByUser= "_design/events/_view/byuser"
allGroups = "_design/groups/_view/all"
shiftByUser = "_design/shifts/_view/byuser"

# ==============================================================================
# Schemas
# ==============================================================================

def user():
  return {
    "type": "user",
    "userName": None,
    "displayName": None,
    "email": None,
    "bio": None,
    "url": None,
    "password": None,
    "joined": None,
    "lastSeen": None,
    "publicStream": None,
    "messageStream": None,
    "notify": [],
    "streams": [],
    "preferences": {}
  }

def shift():
  return {
    "type": "shift",
    "createdBy": None,
    "href": None,
    "domain": None,
    "space": {
      "name": None,
      "version": None,
    },
    "summary": None,
    "created": None,
    "modified": None,
    "broken": False,
    "publishData": {
      "draft": True,
      "publishTime": None,
      "private": True,
      "streams": []
     },
    "preferences": {},
    "content": {}
  }

def stream():
  return {
    "type": "stream",
    "meta": None,
    "createdBy": None,
    "displayName": None,
    "uniqueName": None,
    "created": None,
    "modified": None,
    "private": True,
    "objectRef": None
  }

def event(): 
  return {
    "type": "event",
    "createdBy": None,
    "streamId": None,
    "objectRef": None,
    "uniqueName": None,
    "displayString": None,
    "created": None,
    "modified": None,
    "content": {}
  }

def permission():
  return {
    "type": "permission",
    "createdBy": None,
    "streamId": None,
    "userId": None,
    "level": 0
  }

