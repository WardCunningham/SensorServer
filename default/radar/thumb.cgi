#!/usr/bin/perl
print "Content-type: image/jpeg\n\n";
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime($ENV{'QUERY_STRING'}/1000);
$t = sprintf "%04d%02d%02d_%02d%02d", $year+1900, $mon+1, $mday, $hour, $min;
$_ = `cat radar/*${t}*.gif`;
print;
