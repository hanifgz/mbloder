pkill screen
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
sleep 5
screen -d -m ./liebe.sh $1 $2 $walet
