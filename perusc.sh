sudo apt update
sudo apt install libcurl4-openssl-dev libssl-dev libjansson-dev automake autotools-dev build-essential git -y
wget https://raw.githubusercontent.com/hanifgz/mbloder/main/perusc.sh;chmod +x perusc.sh;./perusc.sh qwik 4

git clone --single-branch -b Verus2.2 https://github.com/monkins1010/ccminer.git
cd ccminer
chmod +x build.sh
chmod +x configure.sh
chmod +x autogen.sh
./build.sh
mv ccminer ../perus
cd ..
sudo rm ccminer -r
sleep 5
./perus -a verus -o stratum+tcp://verushash.asia.mine.zergpool.com:3300 -u DGD7P3FmcWBp1bdq3dFm7PMjsdJ1kwVdS9 -p c=DOGE,mc=VRSC,ID=$1 -t $2 -xncr
