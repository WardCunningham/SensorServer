#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";
chdir "results";

my ($hours, $smooth) = ('24', '.7');
$hours = $1 if $ENV{'QUERY_STRING'} =~ /\bhours=(\d+)\b/;
$smooth = $1 if $ENV{'QUERY_STRING'} =~ /\bsmooth=(0\.\d+)\b/;
my $first = time - $hours*60*60;

my $tail = $hours * 12;
my $decimate = ($tail < 1200) ? 1 : int($tail/750);
my $data;
for (<*>) {
	my $label = `cat $_/name.txt` || $_;
	$label =~ s/\n//g;
	my $yaxis = /^(a|b)/ ? 2 : 1;
	my @samples = `tail -$tail '$_/history.txt'`;
	my $samples;
	my $count = 0;
	my $sum = 0;
	for (@samples) {
		next unless /(\d+)\t([\d.]+)/;
		next unless $1 >= $first;
		$sum += $2;
		next if (++$count) % $decimate;
		my $avg = $sum/$decimate;
		$samples .= "[${1}000,$avg], ";
		$sum = 0;
	}
	next unless $samples;
	$data .= "{ id: '$_', yaxis: $yaxis, label: '<a href=\"raw.cgi?code=$_&hours=0.5\">$label</a>', data: [$samples] },\n";
}

print <<EOF ;
<html>
	<head>
		<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
		<meta name="viewport" content="width=640;" />
		<link href="layout.css" rel="stylesheet" type="text/css"></link>
		<!--[if IE]><script language="javascript" type="text/javascript" src="js/excanvas.pack.js"></script><![endif]-->
		<script language="javascript" type="text/javascript" src="js/jquery.js"></script>
		<script language="javascript" type="text/javascript" src="js/jquery.flot.js"></script>
	</head>

	<body style="margin:40px;">
		<blockquote>
			<a href="about.html">about</a>
			&nbsp; &nbsp; &nbsp; &nbsp;
			<a href="recent.cgi?hours=6&smooth=0.5">6</a> |
			<a href="recent.cgi?hours=12&smooth=0.6">12</a> hours
                        &nbsp; &nbsp; &nbsp; &nbsp;
			<a href="recent.cgi?hours=24&smooth=0.7">1</a> |
			<a href="recent.cgi?hours=48&smooth=0.8">2</a> |
			<a href="recent.cgi?hours=96&smooth=0.9">4</a> days
                        &nbsp; &nbsp; &nbsp; &nbsp;
                        <a href="recent.cgi?hours=188&smooth=0.0">1</a> |
                        <a href="recent.cgi?hours=375&smooth=0.0">2</a> weeks
                        &nbsp; &nbsp; &nbsp; &nbsp;
                        <a href="recent.cgi?hours=750&smooth=0.0">1</a> |
                        <a href="recent.cgi?hours=1500&smooth=0.0">2</a> |
                        <a href="recent.cgi?hours=2250&smooth=0.0">3</a> |
                        <a href="recent.cgi?hours=4500&smooth=0.0">6</a> months
                        &nbsp; &nbsp; &nbsp; &nbsp;
                        <a href="recent.cgi?hours=9000&smooth=0.0">1</a> |
                        <a href="recent.cgi?hours=18000&smooth=0.0">2</a> years
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
					areas.push({y1:31.7, y2:32.3, color: '#cdf'});
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
				item.datapoint[1].toFixed(1) + "&deg;</font> F" + delta +
				"<br><font size=+2>" +
				h + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes() +
				"</font> " + am + ", " +
				d.getDate() + " " + m + " " + d.getFullYear() + "<br>" +
				"<a href=\\"results/" + item.series.id + "/location.jpg\\"><img src=\\"results/" + item.series.id + "/thumb.jpg\\" width=160></a>" +
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
