import time
import datetime

# TODO: adjust for user's actual time - David 7/6/09
def utctime():
  return datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S")
