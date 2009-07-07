import core
import stream

def eventsForStream(streamId):
  return core.query("_design/events/_view/bystream", streamId)


def eventsForUser(userId):
  return core.query("_design/events/_view/byuser", userId)
