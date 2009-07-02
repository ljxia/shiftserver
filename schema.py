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
    "subscriptions": [],
    "streams": [],
    "preferences": {}
  }

def shift():
  return {
    "type": "shift",
    "createdBy": None,
    "href": None,
    "domain": None,
    "space": None,
    "name": None,
    "version": None,
    "summary": None,
    "created": None,
    "modified": None,
    "broken": False,
    "publishData": {
      "draft": True,
      "publishTime": None,
      "private": True
     },
    "streams": [],
    "preferences": {},
    "content": {}
  }

def stream():
  return {
    "type": "stream",
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
    "displayString": None,
    "created": None,
    "modified": None,
    "objectRef": None,
    "content": {}
  }

def permission():
  return {
    "type": "permission",
    "userId": None,
    "level": 0
  }

