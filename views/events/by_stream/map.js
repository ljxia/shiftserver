function (doc)
{
  if(doc.type == "event")
  {
    emit(doc.streamId, doc);
  }
  if(doc.type == "shift")
  {
    for(var i = 0; i < doc.publishData.streams.length; i++)
    {
      emit(doc.publishData.streams[i], doc);
    }
  }
}