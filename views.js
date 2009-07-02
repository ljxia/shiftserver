// =============================================================================
// By Group

function(doc)
{
  var groups = doc.groups;
  for(var i = 0; i < groups.length; i++)
  {
    emit(groups[i], doc);
  }
}

function(key, values, rereduce)
{
  var set = [];
  var seen = [];
  for(var i = 0; i < values.length; i++)
  {
    var _id = values[i]._id;
    if(seen.indexOf(_id) == -1)
    {
      seen.push(_id);
      set.push(values[i]);
    }
  }
  return set;
}
