while true; do
    curl -s http://98.232.243.25:8082/ | tail -1 >>calibration.txt; sleep 30;
done
