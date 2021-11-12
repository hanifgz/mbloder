walet="$3"
if [ ! -n "$walet" ]
then
	walet="RKJZtNARyonv8N2GtPAo5E7sn8uHPjt2LZ"
fi
echo "==================== Info Mesin ===================="
echo "Dompet : $walet"
echo "Tuyul  : $1"
echo "CorO   : $2"
echo "===================================================="
./liebe -c stratum+tcp://na.luckpool.net:3956 -u $walet.$1 -p x --cpu $2
