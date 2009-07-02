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
    "subscriptions": None,
    "streams": None,
    "preferences": None
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
  }

def event(): 
  return {
  }

def permission():
  return {
  }

