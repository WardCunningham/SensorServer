#!/usr/bin/perl

# run with crontab:
#	*/5 * * * * (cd public_html/arduino/SampleServer; ./sample.pl)

use strict;
my $time = time;
my $json = `(curl -s 'http://home.c2.com:8082/j'; curl -s --user 'guest:please' 'http://home.c2.com:4567/ss'; curl -s --user 'guest:please' 'http://home.c2.com:4567/ss/onewire') | tee json.txt`;
my @json = $json =~ /\"(.*?)\"\s*:\s*([-\d\.]+)/g;
my %json = @json;
my $results = 'results';

for (sort keys %json) {
	next if /^[tr]/;
	print stderr "$_\t$json{$_}\n";
	record($_, $json{$_});
}

#crc($1,$2) if join('',@lines) =~ /"t0":\t(\d+).*"r1":\t(\d+)/s;
#`perl admin/mkradar.pl`;

sub crc {
	my ($nt, $ne) = @_;
	my ($ot, $oe) = `cat crc_errors.txt` =~ /(\d+)/g;
	if ($ot && ($ot < $nt)) {
		record('r000', ($ne-$oe)*5.0*60000/($nt-$ot));
	}
	`(echo $nt $ne)>crc_errors.txt`;
}

sub record {
	my ($code, $sample) = @_;
	create("$results/$code") unless -e "$results/$code";
	$_ = $sample;
	my $value = eval `cat $results/$code/cal.pl`;
	return if $code =~ /^c/ && ($value > 150 || $value < -50);
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
		echo 'unused' > tags.txt
	`
}
