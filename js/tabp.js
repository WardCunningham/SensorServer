$(document).ready(function(){
	function tick(ch) {
		$('#activity').html($('#activity').html().replace(/.$/, ch));
	}

	$(document).everyTime(2000, function(i) {
		tick('(');
		$.getJSON("http://98.232.243.25:8082/p?callback=?", function(data){
			tick(')');
			$('#r0').html(data.r0);
			$('#c19356').html(data.c19356/16 * 9/5 + 32);
		});
	});
	
	$('#activity').everyTime(100, function(i) {
		$('#activity').html($('#activity').html().substr(1).concat(i%10?".":","));
	});
});
