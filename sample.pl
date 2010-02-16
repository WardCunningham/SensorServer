#!/usr/bin/perl

# run with crontab:
#	*/5 * * * * (cd public_html/arduino/SampleServer; ./sample.pl)

use strict;

my $time = time;
my @lines = `curl -s 'http://98.232.243.25:8082/j'`;
my $results = 'results';

for (@lines) {
	next unless /"([a-c]\d+)":\s*(\d+),/;
	record($1, $2);
}

sub record {
	my ($code, $sample) = @_;
	create("$results/$code") unless -e "$results/$code";
	$_ = $sample;
	my $value = eval `cat $results/$code/cal.pl`;
	my $round = sprintf("%5.3f", $value);
	open H, ">>$results/$code/history.txt";
	print H "$time\t$round\n";
}

sub create {
	my ($dir) = @_;
	mkdir $dir;
	`	cd $dir;
		echo '\$_ * 1 + 0' > cal.pl
		echo '$dir' > name.txt
		date > info.html
	`
}
