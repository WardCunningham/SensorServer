#!/usr/bin/perl

# run with crontab:
#	*/5 * * * * (cd public_html/arduino/TempServer; ./sample.pl)

use strict;

my $time = time;
my @lines = `curl -s 'http://98.232.243.25:8082/'`;
for (@lines) {
	temp($1) if /^18b20\t(.*)/;
}

sub temp {
	my ($line) = @_;
	my @fields = split /\s+/, $line;
	my %fields = @fields;
	for my $key (keys %fields) {
		$_ = $fields{$key};
		my $value = eval `cat results/$key/cal.pl`;
		record ($key, int($value*100+.5)/100);
	}
}

sub record {
	my ($code, $sample) = @_;
	mkdir "results/$code" unless -e "results/$code";
	open H, ">>results/$code/history.txt";
	print H "$time\t$sample\n";
}
