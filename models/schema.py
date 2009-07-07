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
    "groups": [],
    "following": [],
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
    "streamId": None,
    "userId": None,
    "level": 0
  }

