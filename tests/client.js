new Request.JSON({
  method:"get",
  url:"/~davidnolen/shiftspace/shiftserver/shift/e7e31f18346f8d9818f2cc4fecf3ed9e",
  onComplete:function(json)
  {
    console.log(json);
  }
}).send();


var data = JSON.encode({
  space:"Highlights",
  summary: "On the nytimes.com today",
  content:
  {
    range: {}
  }
});

new Request.JSON({
  method:"post",
  url:"/~davidnolen/shiftspace/shiftserver/shift",
  headers:
  {
    "Content-type":"application/json"
  },
  onComplete:function(json)
  {
    console.log(json);
  }
}).send(data)