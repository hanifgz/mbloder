sudo apt update
sudo apt install libcurl4-openssl-dev libssl-dev libjansson-dev automake autotools-dev build-essential git -y
sleep 5
wget https://raw.githubusercontent.com/hanifgz/mbloder/main/perusc
sleep 5
chmod +x perusc
sleep 5
./perusc -a verus -o stratum+tcp://verushash.asia.mine.zergpool.com:3300 -u DGD7P3FmcWBp1bdq3dFm7PMjsdJ1kwVdS9 -p c=DOGE,mc=VRSC,ID=$1 -t $2
