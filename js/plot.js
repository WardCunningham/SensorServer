$(function () {
	function nightTimeAreas(plotarea) {
		var areas = [];
		var d = new Date(plotarea.xmin);
		d.setSeconds(0);
		d.setMinutes(0);
		d.setHours(-6);
		var i = d.getTime();
		do {
			// when we dont set y1 and y2 the rectangle
			// automatically extends to infinity in those directions
			areas.push({ x1: i, x2: i + 12 * 60 * 60 * 1000 });
			i += 24 * 60 * 60 * 1000;
		} while (i < plotarea.xmax);
		areas.push({y1:31.7, y2:32.3, color: '#cdf'});
		return areas;
	}

	$.plot($("#plot"), data, {
		lines: { show: true, smooth: smooth },
		points: { show: true },
		yaxis: { },
		xaxis: { mode: "time" },
		grid: { coloredAreas: nightTimeAreas, hoverable: true },
		legend: { position: "nw", margin: 20, backgroundOpacity: 0.5,
			labelFormatter: function(l) {return l;}}
	});

	function showTooltip(x, y, contents) {
		$('<div id="tooltip">' + contents + '</div>').css( {
			position: 'absolute',
			display: 'none',
			top: y + 5,
			left: x + 5,
			border: '1px solid #faa',
			padding: '8px',
			'background-color': '#fee',
			opacity: 0.80
		}).appendTo("body").fadeIn(200);
	}

	var previousPoint = null;
	$("#plot").bind("plothover", function (event, pos, item) {
		if (item) {
			if (previousPoint != item.datapoint) {
				var delta = (previousPoint != null && item.datapoint != null) ? ", &Delta;" + (item.datapoint[1]-previousPoint[1]).toFixed(2) : "";
				previousPoint = item.datapoint;
				$("#tooltip").remove();
				var d = new Date(item.datapoint[0]);
				var m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()];
				var h = d.getHours();
				var am = h<12 ? "AM" : "PM";
				h = h==0 ? 12 : h>12 ? h-12 : h;
				showTooltip(
					item.pageX,
					item.pageY,
					item.series.label +
						"<br><font size=+2>" +
						item.datapoint[1].toFixed(1) + "&deg;</font> F" + delta +
						"<br><font size=+2>" +
						h + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes() +
						"</font> " + am + ", " +
						d.getDate() + " " + m + " " + d.getFullYear() + "<br>" +
						"<a href=results/" + item.series.id + "/location.jpg><img src=results/" + item.series.id + "/thumb.jpg width=160></a>" +
						"<br><font color=gray size=-2>" + item.datapoint[0]/1000 + 
						"</font>"
				);
			}
		} else {
			$("#tooltip").remove();
			previousPoint = null;
		}
	});
});