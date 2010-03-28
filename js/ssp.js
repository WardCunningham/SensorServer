$(document).ready(function(){
	var wave = [];
	var n = 0;
	var patt=/\b[abctr]\d+$/;
	var chan=patt.exec(window.location.href);
	$(document).everyTime(1000, function(i) {
		$.getJSON("http://98.232.243.25:8082/p?callback=?", function(element){
			if (n==0) {n = (new Date()).valueOf() - (element.t0 - element.t1);}
			if (wave.length >= 300) {wave.shift();}
			wave.push(element);
			var data = {};
			for (var w = 0; w<wave.length; w++) {
				var sample = wave[w];
				var x = n + sample.t0 - sample.t1;
				for (i in sample) {
					if(chan!=null) {
						if(i!=chan) {continue}
					} else {
						if(i.match(/t|r/)) {continue;}
					}
					if(data[i]==undefined) {data[i]=new Array(30);}
					data[i].push([x, sample[i]]);
				}
			}
			var plot_data = [];
			for (i in data) {
				plot_data.push({ label: i, data: data[i] });
			}
			$.plot($("#plot"), plot_data, { xaxis: { mode: "time" }, legend: { position: "nw"} });
			$("#stat").html(
				"<br>elapsed time: " + element.t0/1000 +
				"<br>requests served: " + element.r0 +
				"<br>1-wire crc errors: " + element.r1);
		});
	});
});

