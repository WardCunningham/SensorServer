# remove glitches (temp > 150) from history files

for i in results/c*/history.txt; do echo $i; perl -i -ne 'print unless /\t(\d+)/ && $1 > 150' $i; done
