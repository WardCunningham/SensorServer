#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";


print << ;
	<head>
	<meta name="viewport" content="width=640;" />
	</head>
	<body style="margin:40px;">
	<a href="about.html">about</a> |
	<a href="recent.cgi">plot</a> |
	<a href="results">data</a>
	<table cellpadding=10 cellspacing=0 width=560>

chdir "results";

for (<*>) {
	my $info = `cat $_/info.html` if -e "$_/info.html";
	my $name = `cat $_/name.txt` if -e "$_/name.txt";
	$name = "<br>$name" if $name;
	next unless `tail -1 '$_/history.txt'` =~ /(\d+)\t([\d.]+)\b/;
	my $temp = sprintf("%.1f",$2);
	my $age = int((time - $1)/3600);
	$age = $age ? "<br>off $age hr" : '';
	print <<;
		<tr><td>
		<tr bgcolor=#eeeeee>
		<td align=center>&nbsp;
			<a href="recent.cgi?code=$_"><font size=24>$temp&deg;</font></a>
			$name
			<br><font color=gray>$_ $age</font>
		<td><a href="results/$_/location.jpg"><img src="results/$_/thumb.jpg"></a>
		<td>$info

}

print <<;
	</table>


