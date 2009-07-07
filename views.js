// =============================================================================
// groups
// =============================================================================

// all
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    var groups = doc.groups;
    for(var i = 0; i < groups.length; i++)
    {
      emit(groups[i], doc);
    }
  }
}

// =============================================================================
// users
// =============================================================================

// by_name
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    emit(doc.userName, doc);
  }
}

// =============================================================================
// shifts
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc) {
  if(doc.type == "shift")
  {
    emit(doc._id, doc);
  }
}

// by_user
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "shift")
  {
    emit(doc.createdBy, doc);
  }
}

// by_href
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "shift")
  {
    emit(doc.href, doc);
  }
}

// by_domain
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit("http://"+parts[0], doc);
  }
}

// by_user_and_domain
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "shift")
  {
    var href = doc.href;
    var url = href.substr(7, href.length);
    var parts = url.split("/");
    emit([doc.createdBy, "http://"+parts[0]], doc);
  }
}

// =============================================================================
// streams
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc._id, doc);
  }
}

// subscribers
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "user")
  {
    var streams = doc.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit(streams[i], doc);
    }
  }
}

// by_object_ref
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.objectRef, doc);
  }
}

// by_unique_name
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.uniqueName, doc);
  }
}

// stream_with_events
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "user")
  {
    streams = doc.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit([stream[i], 0]);
    }
  }
  else if(doc.type == "event")
  {
    emit([doc.streamId, 1]);
  }
}

// event_with_shift
// -----------------------------------------------------------------------------
function (doc)
{
  var objectRef = doc.objectRef;
  if(doc.type == "event" && objectRef)
  {
    var parts = objectRef.split(":");
    if(parts[0] == "shift")
    {
      emit([parts[1], 0], doc);
    }
  }
  else if(doc.type == "shift")
  {
    emit([doc._id, 1], doc);
  }
}

// We should reduce the two things into one value

// =============================================================================
// events
// =============================================================================

// by_stream
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc.streamId, doc);
  }
}

// by_user
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc.createdBy, doc);
  }
}

// for_user
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "user")
  {
    
  }
}

// =============================================================================
// permissions
// =============================================================================

// by_user
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc.userId, doc);
  }
}
