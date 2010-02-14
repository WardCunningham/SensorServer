$(document).ready(function(){
	var wave = [];
	var n = 0;
	$(document).everyTime(1000, function(i) {
		$.getJSON("j", function(element){
			if (wave.length >= 300) {wave.shift();}
			wave.push([n++,element]);
			var data = {};
			for (var w = 0; w<wave.length; w++) {
				var x = wave[w][0];
				var sample = wave[w][1];
				for (i in sample) {
					if(i.match(/t|r/)) {continue;}
					if(data[i]==undefined) {data[i]=new Array(30);}
					data[i].push([x, sample[i]]);
				}
			}
			var plot_data = [];
			for (i in data) {
				plot_data.push(data[i]);
			}
			$.plot($("#plot"), plot_data);
			$("#stat").html(
				"<br>elapsed time: " + element.t0/1000 +
				"<br>requests served: " + element.r0 +
				"<br>1-wire crc errors: " + element.r1);
		});
	});
});

