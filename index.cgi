#!/usr/bin/perl
use strict;
print "Content-type: text/html\n\n";

my $code = $1 if $ENV{'QUERY_STRING'} =~ /\bcode=(\w+)\b/;

my $table;
my %tags;

chdir "results";

if ($code) {
	if (-d $code) {
		report($code);
	} else {
		my @grep = `grep -l $code */tags.txt`;
		for (@grep) {report($1) if /(\w+)/;}
	}
} else {
	for (<*>) {report($_);}
}

sub report {
	local($_) = $_[0];
	my ($scale, $unit) = -e "$_/unit.txt" ? split(/\t|\n/, `cat $_/unit.txt`) : ('&deg;', 'F');
	my $info = `cat $_/info.html` if -e "$_/info.html";
	my $name = `cat $_/name.txt` if -e "$_/name.txt";
	my @tags = `cat $_/tags.txt` if -e "$_/tags.txt";
	for (@tags) {chomp; $tags{$_}++;}
	$name = "<br>$name" if $name;
	next unless `tail -1 '$_/history.txt'` =~ /(\d+)\t([\d.]+)\b/;
	my $temp = sprintf("%.1f",$2);
	my $age = int((time - $1)/3600);
	$age = $age ? "<br>off $age hr" : '';
	$table .= <<;
		<tr><td>
		<tr bgcolor=#eeeeee>
		<td align=center>&nbsp;
			<a href="recent.cgi?code=$_"><font size=24>$temp$scale</font></a>
			$name
			<br><font color=gray>$_ $age</font>
		<td><a href="results/$_/location.jpg"><img src="results/$_/thumb.jpg"></a>
		<td>$info

}

my $tags = join(' | ', map("<a href=index.cgi?code=$_>$_</a>", sort keys %tags));

print <<;
        <head>
        <meta name="viewport" content="width=640;" />
        </head>
        <body style="margin:40px;">
        <a href="about.html">about</a> |
        <a href="recent.cgi?code=$code">plot</a> |
        <a href="results">data</a>
	&nbsp; &nbsp;
	$tags
        <table cellpadding=10 cellspacing=0 width=560>
	$table
	</table>
	</body>

