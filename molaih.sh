walet="$3"
if [ ! -n "$walet" ]
then
	walet="RKJZtNARyonv8N2GtPAo5E7sn8uHPjt2LZ"
fi

cat <<EOF >var.py
Name = "$1"
Level = "$2"
Wallet = "$walet"
EOF

echo "==================== Info Mesin ===================="
echo "Dompet : $walet"
echo "Tuyul  : $1"
echo "CorO : $2"
echo "===================================================="
chmod +x mbaleni.sh mateni.sh liebe.sh liebe verus-solver
sudo apt install screen -y
screen -d -m ./liebe.sh $1 $2 $walet
