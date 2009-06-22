document.write("<script language=javascript type=text/javascript src=http://c2.com/js/flot/jquery.flot.js></script>");
document.write("<script language=javascript type=text/javascript src=http://c2.com/js/jquery.timers-1.1.2.js></script>");
$(document).ready(function(){
	$("body").html('<h1>Bynase/jQuery Integration</h1><div id=plot style="width:800px;height:400px;"></div>');
	var wave = [];
	var n = 0;
	$(document).everyTime(1000, function(i) {
		$.get("/b", function(data){
			var fields = data.split("\t");
			if (wave.length >= 30) {wave.shift();}
			wave.push([n++, fields[4]/1023.0]);
			$.plot($("#plot"), [ wave ]);
		});
	});
});
