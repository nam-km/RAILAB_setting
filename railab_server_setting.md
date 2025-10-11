## Step 0. Setup
- reservation: http://143.248.6.101:24/
- server information
```
ssh user@143.248.6.83 (password: hubo)
ssh railab@143.248.6.101/105 (password: railab)
ssh user@143.248.6.168 (password: railab)
ssh user@143.248.249.145/146 (password: raiboisKing)
ssh user@143.248.249.67/108 (password: RaiboisKing)
ssh user@143.248.8.10 (password: raiboisKing)
ssh user@143.248.247.189 (password: raiboisKing)
ssh user@143.248.247.137/138 (password: raiboisKing)
```
- add my account `nkm`

```
ssh user@143.248.6.83
sudo su
adduser nkm
sudo usermod -aG docker nkm
exit
```
- add git ssh in nkm@143.248.6.83
```
# exit user and log in as nkm
ssh-keygen
cat .ssh/id_rsa.pub
git clone git@github.com:railabatkaist/Railab_Manual.git
```

- modify Dockerfile, runner.bash  
```
cd Railab_Manual/raisim_docker

nano Dockerfile 
# modify 6006 to 4444  
# You may check cuda version, ubuntu version of server (11.8, 22.04)
# You may remove "-8" of "gcc-8 g++-8" if you have error
# You may change 3.9 to 3.10

nano runner.bash
# modify 6006:6006 to 4444:4444, rsg to nkm  

docker build -t nkm .
# . to navigate `Railab_Manual/raisim_docker`  

bash runner.bash

docker ps -a 
# you can see name of nkm is initialized to random (ex. loving_matsumoto)
docker rename loving_matsumoto nkm
docker ps -a
# you can see name of nkm is nkm

exit
# back to local
```

- How to start docker


```
# at local, go to server
nkm@nkm-com2:~$ ssh nkm@143.248.6.83
nkm@nkm-com2:~$ ssh -L 4444:localhost:4444 nkm@143.248.6.105

#then,nkm@user-TRX40-DESIGNARE:~$ 

# at server, go to docker
nkm@user-TRX40-DESIGNARE:~$ docker start nkm
nkm@user-TRX40-DESIGNARE:~$ docker attach nkm

# then, root@4442112939a3:/# 
```

- basic setting
```
update-alternatives --install /usr/bin/python python /usr/bin/python3 1

apt update
apt upgrade
apt install libopencv-dev
pip install "ruamel.yaml<0.18.0"
pip install numpy==1.26.4 tensorboard==2.18.0
pip install torch
```

- add raisim activation key
```
git clone git@github.com:KyeongminNam/RAILAB_setting.git
mkdir /root/.raisim
mv RAILAB_setting/activation.raisim /root/.raisim/
```


- Some useful commands
```
git clone git@github.com:KyeongminNam/raisimGymForSegway.git
python setup.py develop --CMAKE_PREFIX_PATH ../raisimLib/raisim/linux
git checkout -- .

```

## 1. How to transer file btw docker & local

- from docker to server  
nkm@user-TRX40-DESIGNARE:~$ `docker cp nkm:/root/aaa .`  
`docker cp nkm:/root/../raisim_ws/raisimGymForSegway/raisimGymForSegway/data/ .`


- from server to docker  
nkm@user-TRX40-DESIGNARE:~$ `docker cp aaa nkm:/root`  
`docker cp 2025-02-13-11-48-37/ nkm:/root/../raisim_ws/raisimGymForSegway/raisimGymForSegway/data/transfer`

- from server to local  
nkm@nkm-com2:~$ `scp nkm@143.248.6.83:aaa .`  
when moving folder, add option `-r`  
`scp -r nkm@143.248.6.105:data/raiway_sit_down_GRU/ .`

- from local to server  
nkm@nkm-com2:~$ `scp aaa nkm@143.248.6.83`
`scp -r /home/nkm/raisim_ws/raisimGymForSegway/raisimGymForSegway/data/raiway_sit_down_GRU_4/2025-02-13-11-48-37/ nkm@143.248.6.105:~/  `
`scp -r raisimGymForSegway/data/raiway_sit_down_GRU_4/2025-02-24-11-46-04/ nkm@143.248.6.101:data_transfer/`


## 2. Error

#### 1) RuntimeError: No CUDA GPUs are available

```
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio
```

```
ls -l /tmp/.docker.xauth
# total 0

file /tmp/.docker.xauth
# /tmp/.docker.xauth: directory

sudo rm -rf /tmp/.docker.xauth
sudo touch /tmp/.docker.xauth

ls -l /tmp/.docker.xauth
# -rw-r--r-- 1 root root 0 Jul 13 01:13 /tmp/.docker.xauth
```