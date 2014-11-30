#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";
chdir "results/a2010";

my ($hours, $smooth, $slope) = ('528', '0.5', 'am');
$hours = $1 if $ENV{'QUERY_STRING'} =~ /\bhours=(\d+)\b/;
$smooth = $1 if $ENV{'QUERY_STRING'} =~ /\bsmooth=(0\.\d+)\b/;
$slope = $1 if $ENV{'QUERY_STRING'} =~ /\bslope=(\w+)\b/;
my $first = time - $hours*60*60;

my $tail = $hours * (60/5);
my @samples = `tail -$tail 'history.txt'`;
my %samples;
for (@samples) {
	next unless /(\d+)\t(\d+\.\d)/;
	next unless $1 >= $first;
	my $temp = ($2-50)*10;
	my $track = $1/(5*60) % (24*12);
	$track = (int($track/12)*100) + (($track%12)*5);
	next if $track < 600 && $slope eq 'am';
	next if $track > 600 && $slope eq 'pm';
	$samples{$track} .= "[${1}000,$temp], ";
}


my $data;
for (sort {$a <=> $b} keys %samples) {
	next unless $samples{$_} =~ /,[2-6]\d/;
	my $color = $_ < 600 ? 4 : 5;
	$data .= "{ id: '$_', color: $color, label: '$_', data: [";
	$data .= $samples{$_};
	$data .= "] },\n\n";
}

print <<EOF ;
<html>
	<head>
		<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
		<link href="layout.css" rel="stylesheet" type="text/css"></link>
		<!--[if IE]><script language="javascript" type="text/javascript" src="/js/flot/excanvas.pack.js"></script><![endif]-->
		<script language="javascript" type="text/javascript" src="/js/flot/jquery.js"></script>
		<script language="javascript" type="text/javascript" src="/js/flot/jquery.flot.js"></script>
	</head>

	<body style="margin:40px;">
		<h1>Daylight Isolumes (arrival of twilight, day by day)</h1>
		<blockquote>
			<a href="about.html">about</a>
			&nbsp; &nbsp; &nbsp; &nbsp;
			<a href="twilight.cgi?hours=192&smooth=$smooth&slope=$slope">1</a> |
			<a href="twilight.cgi?hours=360&smooth=$smooth&slope=$slope">2</a> |
			<a href="twilight.cgi?hours=528&smooth=$smooth&slope=$slope">3</a> |
			<a href="twilight.cgi?hours=696&smooth=$smooth&slope=$slope">4</a> |
			<a href="twilight.cgi?hours=864&smooth=$smooth&slope=$slope">5</a> weeks
			&nbsp; &nbsp; &nbsp; &nbsp;
			<a href="twilight.cgi?hours=$hours&smooth=$smooth&slope=am">am</a> |
			<a href="twilight.cgi?hours=$hours&smooth=$smooth&slope=pm">pm</a> |
			<a href="twilight.cgi?hours=$hours&smooth=$smooth&slope=both">both</a>
			&nbsp; &nbsp; &nbsp; &nbsp;
			<a href="twilight.cgi?hours=$hours&smooth=0.0&slope=$slope">no</a> |
			<a href="twilight.cgi?hours=$hours&smooth=0.5&slope=$slope">low</a> |
			<a href="twilight.cgi?hours=$hours&smooth=0.9&slope=$slope">high</a> smoothing
		</blockquote>
		<div id="placeholder" style="width:95%;height:85%;"></div>
		<script id="source" language="javascript" type="text/javascript">
			\$(function () {
				var data = [$data];
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
					areas.push({y1:49.7, y2:50.3, color: '#ccc'});
					return areas;
				}
				\$.plot(\$("#placeholder"), data, {
					lines: { show: true, smooth: $smooth },
					points: { show: true },
					yaxis: { },
					xaxis: { mode: "time" },
					grid: { coloredAreas: nightTimeAreas, hoverable: true },
					legend: { position: "nw", margin: 20, backgroundOpacity: 0.5,
						labelFormatter: function(l) {return l;}}
				});

    function showTooltip(x, y, contents) {
        \$('<div id="tooltip">' + contents + '</div>').css( {
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
    \$("#placeholder").bind("plothover", function (event, pos, item) {
            if (item) {
                if (previousPoint != item.datapoint) {
                    var delta = (previousPoint != null && item.datapoint != null) ? ", &Delta;" + (item.datapoint[1]-previousPoint[1]).toFixed(2) : "";
                    previousPoint = item.datapoint;
                    \$("#tooltip").remove();
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
				item.datapoint[1].toFixed(1) + "%</font> light" + delta +
				"<br><font size=+2>" +
				h + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes() +
				"</font> " + am + ", " +
				d.getDate() + " " + m + " " + d.getFullYear() + "<br>" +
				"<a href=\\"results/light/location.jpg\\"><img src=\\"results/light/thumb.jpg\\" width=160></a>" +
				"<br><font color=gray size=-2>" + item.datapoint[0]/1000 + "</font>");
                }
            }
            else {
                \$("#tooltip").remove();
                previousPoint = null;
            }
    });


			});
		</script>
	</body>
</html>
EOF
