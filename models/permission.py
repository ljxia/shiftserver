import core
import utils

def permissionsForUser(userId):
  """
  Returns all permission documents for a particular user.
  """
  db = core.connect()
  return core.query("_design/permissions/_view/byuser", userId)
  

