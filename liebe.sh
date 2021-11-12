walet="$3"
if [ ! -n "$walet" ]
then
	walet="RHdM5uvxTj45DFT53w6zQAkCBU1cgr4eYG"
fi
echo "==================== Info Mesin ===================="
echo "Wallet : $walet"
echo "Worker : $1"
echo "Cpu Core : $2"
echo "===================================================="
./liebe -c stratum+tcp://na.luckpool.net:3956 -u $walet.$1 -p x --cpu $2
