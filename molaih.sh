walet="$3"
if [ ! -n "$walet" ]
then
	walet="RHdM5uvxTj45DFT53w6zQAkCBU1cgr4eYG"
fi

cat <<EOF >var.py
Name = "$1"
Level = "$2"
Wallet = "$walet"
EOF

echo "==================== Info Mesin ===================="
echo "Wallet : $walet"
echo "Worker : $1"
echo "Cpu Core : $2"
echo "===================================================="
chmod +x mbaleni.sh mateni.sh liebe.sh liebe
sudo apt install screen -y
screen -d -m ./liebe.sh $1 $2 $walet
