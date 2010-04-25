#!/usr/bin/perl
print "Content-type: image/jpeg\n\n";
$_ = `cat thumb.jpg`;
print;
