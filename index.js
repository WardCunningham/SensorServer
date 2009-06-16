document.write("<script language=javascript type=text/javascript src=http://c2.com/js/flot/jquery.flot.js></script>");
document.write("<script language=javascript type=text/javascript src=http://c2.com/js/jquery.timers-1.1.2.js></script>");
$(document).ready(function(){
	$("body").html("<h1>Bynase/jQuery Integration</h1><pre><span id=sample>data goes here</span></pre>");
	$(document).everyTime(1000, function(i) {
	  $("#sample").load("/g");
	  }, 0, true);
});
//document.write("</head><body><h1>Bynase/jQuery Integration</h1><pre><span id=sample>data goes here</span></pre>");
