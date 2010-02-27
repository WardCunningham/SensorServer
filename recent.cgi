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
		<script language="javascript" type="text/javascript" src="js/plot.js"></script>
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
		<div id="plot" style="width:95%;height:85%;"></div>
		<script id="source" language="javascript" type="text/javascript">
			var data = [$data];
			var smooth = $smooth;
		</script>
	</body>
</html>
EOF
