pkill screen
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
sleep 5
screen -d -m ./liebe.sh $1 $2 $walet
