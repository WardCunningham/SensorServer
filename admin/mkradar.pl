use Time::Local;

open F, ">results/rtx/history.txt";
for (<radar/*.gif>) {
	next unless /(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)/;
	$t = timegm 0, $5, $4, $3, $2-1, $1;
	$s = (-s $_) / 1000;
	print F "$t\t$s\n";
}
