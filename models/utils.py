import time
import datetime


def ids(rows):
  return [row["_id"] for row in rows]


def genrefn(pre):
  def refn(id, post=None):
    if post:
      return ":".join([pre, id, post])
    else:
      return ":".join([pre, id])
  return refn

# TODO: adjust for user's actual time - David 7/6/09
def utctime():
  return datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S")
