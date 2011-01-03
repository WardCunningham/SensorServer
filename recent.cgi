#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";
chdir "results";

my ($hours, $smooth, $code) = ('24', '.7', '');
$hours = $1 if $ENV{'QUERY_STRING'} =~ /\bhours=(\d+)\b/;
$smooth = $1 if $ENV{'QUERY_STRING'} =~ /\bsmooth=(0\.\d+)\b/;
my $code = $1 if $ENV{'QUERY_STRING'} =~ /\bcode=(\w+)\b/;

my $first = time - $hours*60*60;
my $tail = $hours * 12;
my $decimate = ($tail < 1200) ? 1 : int($tail/750);
my $data;

if ($code) {
	if (-d $code) {
		transform($code);
	} else {
		my @grep = `grep -l $code */tags.txt`;
		for (@grep) {transform($1) if /(\w+)/;}
	}
} else {
	for (<*>) {transform($_)}
}

sub transform {
	local($_) = $_[0];
	my $label = `cat $_/name.txt` || $_;
	$label =~ s/\n//g;
	my ($scale, $unit) = -e "$_/unit.txt" ? split(/\t|\n/, `cat $_/unit.txt`) : ('&deg;', 'F');
	my $yaxis = /^(a|b|r)/ ? 2 : 1;
	my @samples = `tail -$tail '$_/history.txt'`;
	my ($samples, $last, $count, $sum) = ('', '', 0, 0);
	for (@samples) {
		next unless /(\d+)\t([\d.]+)/;
		next unless $1 >= $first;
		$sum += $2;
		next if (++$count) % $decimate;
		my $avg = $sum/$decimate;
		if ($last && ($1-$last)>(300*$decimate+3300)) {
			my $missing = int(($1+$last)/2);
			$samples .= "[${missing}000,null], ";
		}
		$last = $1;
		$samples .= "[${1}000,$avg], ";
		$sum = 0;
	}
	next unless $samples;
	$data .= "{
		id: '$_',
		yaxis: $yaxis,
		label: '<a href=\"recent.cgi?code=$_&hours=$hours\">$label</a>',
		scale: '$scale',
		unit: '$unit',
		data: [$samples],
	},";
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
			<a href="recent.cgi?code=$code&hours=6&smooth=0.5">6</a> |
			<a href="recent.cgi?code=$code&hours=12&smooth=0.6">12</a> hours
			&nbsp;
			<a href="recent.cgi?code=$code&hours=24&smooth=0.7">1</a> |
			<a href="recent.cgi?code=$code&hours=48&smooth=0.8">2</a> |
			<a href="recent.cgi?code=$code&hours=96&smooth=0.9">4</a> days
			&nbsp;
			<a href="recent.cgi?code=$code&hours=188&smooth=0.0">1</a> |
			<a href="recent.cgi?code=$code&hours=375&smooth=0.0">2</a> weeks
			&nbsp;
			<a href="recent.cgi?code=$code&hours=750&smooth=0.0">1</a> |
			<a href="recent.cgi?code=$code&hours=1500&smooth=0.0">2</a> |
			<a href="recent.cgi?code=$code&hours=2250&smooth=0.0">3</a> |
			<a href="recent.cgi?code=$code&hours=4500&smooth=0.0">6</a> months
			&nbsp;
			<a href="recent.cgi?code=$code&hours=9000&smooth=0.0">1</a> |
			<a href="recent.cgi?code=$code&hours=18000&smooth=0.0">2</a> years
		</blockquote>
		<div id="plot" style="width:95%;height:85%;"></div>
		<script id="source" language="javascript" type="text/javascript">
			var smooth = $smooth;
			var data = [$data];
		</script>
	</body>
</html>
EOF
