$url = 'http://radar.weather.gov/ridge/RadarImg/NCR/RTX/';
@index = `curl -s $url`;
for (@index) {
	next unless /href="(..._........_...._....gif)"/;
	next if -e "radar/$1";
	`curl -s $url/$1 >radar/$1`;
	`rm radar/$1` if 952 == -s "radar/$1";
}
