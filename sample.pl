#!/usr/bin/perl

# run with crontab:
#	*/5 * * * * (cd public_html/arduino/SampleServer; ./sample.pl)

use strict;

my $time = time;
my @lines = `curl -s 'http://98.232.243.25:8082/g'`;
for (@lines) {
	temp($1) if /^18b20\t(.*)/;
	pin(0,'a',$1) if /^analog\t(.*)/;
	pin(1,'a',$1) if /^analog\t(.*)/;
	pin(3,'b',$1) if /^bynase\t(.*)/;
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

sub pin {
	my ($pin, $code, $line) = @_;
	my @fields = split /\s+/, $line;
	$_ = @fields[$pin];
	my $value = eval `cat results/$code$pin/cal.pl`;
	record ("$code$pin", sprintf("%5.3f", $value));
}

sub record {
	my ($code, $sample) = @_;
	mkdir "results/$code" unless -e "results/$code";
	open H, ">>results/$code/history.txt";
	print H "$time\t$sample\n";
}
