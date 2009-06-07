for i in results/*
do echo $i
	convert -size 160x120 "$i/location.jpg" -resize 160x120 +profile "*" "$i/thumb.jpg"
done
