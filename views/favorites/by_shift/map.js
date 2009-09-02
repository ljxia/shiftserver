function(doc) {
  if(doc.type == "favorite")
  {
     emit(doc._id.split(":")[2], 1);
  }
}