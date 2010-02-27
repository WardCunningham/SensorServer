@lines = `cat calibration.txt`;
for (@lines) {
	@fields = split /\s+/;
	shift @fields;
	%fields = @fields;
	for (keys %fields) {
		$sum{$_} += $fields{$_};
		$sum += $fields{$_};
		$fields++;
	}
	$lines++;
}

mkdir "results" or die $! unless -e "results";
$true = $sum/$fields;
for (sort keys %sum) {
	$avg = $sum{$_}/$lines;
	$delta = $true - $avg;
	print "$_\t$delta\n";
	mkdir "results/$_" or die $! unless -e "results/$_";
	open F, ">results/$_/cal.pl";
	print F "(\$_+$delta)/16.0*1.8+32\n";
}
