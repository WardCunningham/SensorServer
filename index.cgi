#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";


print <<;
	<body style="margin:40px;">
	<a href="about.html">about</a> |
	<a href="recent.cgi">plot</a> |
	<a href="results">data</a>
	<table cellpadding=10 cellspacing=0>


chdir "results";

for (<*>) {
	my $info = `cat '$_/info.html'` if -e "$_/info.html";;
	my $temp = $1 if `tail -1 '$_/history.txt'` =~ /\b(\d+\.\d+)\b/;
	print <<;
		<tr><td>
		<tr bgcolor=#eeeeee>
		<td>&nbsp; <a href="raw.cgi?code=$_&hours=0.5&smooth=0.9"><font size=24>$temp&deg;</font></a>
		<td><a href="results/$_/location.jpg"><img src="results/$_/thumb.jpg"></a>
		<td valign=top><font size=-1><pre>$info</pre></font>

}

print <<;
	</table>


