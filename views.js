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

// all
// ------------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "all")
  {
    emit(doc._id, doc);
  }
}


// by_name
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    emit(doc.userName, doc);
  }
}

// join_shifts
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    emit([doc._id, 0], doc);
  }
  else if(doc.type == "shift")
  {
    emit([doc.createdBy, 1], doc);
  }
}

// notify
// -----------------------------------------------------------------------------
function(doc)
{
  if(doc.type == "user")
  {
    for(var i = 0; i < doc.notify.length; i++)
    {
      emit(doc.notify[i], doc._id);
    }
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

// by_stream
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "shift")
  {
    var streams = doc.publishData.streams;
    for(var i = 0; i < streams.length; i++)
    {
      emit(streams[i], doc);
    }
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

// comments
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "stream" &&
     doc.meta == "comments")
  {
    var parts = doc.objectRef.split(":");
    if(parts[0] == "shift") emit(parts[1], doc);
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

// by_creator
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "stream")
  {
    emit(doc.createdBy, doc)
  }
}

// We should reduce the two things into one value

// =============================================================================
// events
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "event")
  {
    emit(doc._id, doc);
  }
}

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

// =============================================================================
// permissions
// =============================================================================

// all
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc._id, doc);
  }
}

// by_user
// -----------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc.userId, doc);
  }
}

// by_user_and_stream
// ------------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "permission")
  {
    emit([doc.userId, doc.streamId], doc);
  }
}

// by_stream
// ------------------------------------------------------------------------------
function (doc)
{
  if(doc.type == "permission")
  {
    emit(doc.streamId, doc);
  }
}

// =============================================================================
// validation
// =============================================================================

function(newDoc, oldDoc, userCtx)
{
  if(newDoc &&
     newDoc.type &&
     oldDoc)
  {
    if(newDoc.type != oldDoc.type)
    {
      throw {changing_type: 'Document cannot change type. ' + newDoc.type + ' -> ' + oldDoc.type};
    }
    if(newDoc.createdBy && (newDoc.createdBy != oldDoc.createdBy))
    {
      throw {changing_owner: 'You cannot change the owner of the document.'};
    }
    if(newDoc.created && (newDoc.created != oldDoc.created))
    {
      throw {changing_created: 'You cannot change the created field of the document.'};
    }
    if(newDoc.uniqueName && (newDoc.uniqueName != oldDoc.uniqueName))
    {
      throw {changing_unique_name: 'You cannot change the uniqueName field of a document.'};
    }
    if(newDoc.type == 'event')
    {
      if(newDoc.objectRef != oldDoc.objectRef)
      {
	throw {changing_objectref: 'You cannot change the objectRef of an event.'};
      }
      if(newDoc.streamId != oldDoc.streamId)
      {
	throw {rehost_event: 'You cannot rehost an event to another stream.'};
      }
    }
  }
}
