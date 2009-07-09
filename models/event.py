import core
import stream
import schema

def eventsForStream(streamId):
  return core.query(schema.eventByStream, streamId)


def eventsForUser(userId):
  return core.query(schema.eventByUser, userId)
