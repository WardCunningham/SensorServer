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
	my $temp = sprintf("%.1f",$1) if `tail -1 '$_/history.txt'` =~ /\t([\d.]+)\b/;
	print <<;
		<tr><td>
		<tr bgcolor=#eeeeee>
		<td align=center>&nbsp;
			<a href="raw.cgi?code=$_&hours=0.5&smooth=0.9"><font size=24>$temp&deg;</font></a>
			<br>$name
			<br><font color=gray>$_</font>
		<td><a href="results/$_/location.jpg"><img src="results/$_/thumb.jpg"></a>
		<td>$info

}

print <<;
	</table>


