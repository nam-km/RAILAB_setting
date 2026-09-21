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
git clone git@github.com:KyeongminNam/RAILAB_setting.git
```

- modify Dockerfile, runner.bash  
- put your name in [nkm]
```
cd RAILAB_setting/server_setting

vim Dockerfile
# modify 6006 to 4444  
# You may check cuda version, ubuntu version of server (11.8, 22.04)
# You may remove "-8" of "gcc-8 g++-8" if you have error
# You may change 3.9 to 3.10

vim runner.bash
# modify 6006:6006 to 4444:4444, rsg to nkm

docker build -t nkm .
# . to navigate `RAILAB_setting/server_setting`  

bash runner.bash

docker ps -a 
# you can see name of nkm is initialized to random (ex. loving_matsumoto)
docker rename loving_matsumoto nkm
docker ps -a
# you can see name of nkm is nkm

exit
# back to local
```

- If you are using Raisim2
```
vim Dockerfile2
vim runner.bash

docker build -f Dockerfile2 -t nkm2 .
bash runner.bash
docker ps -a 
docker rename loving_matsumoto nkm2
docker ps -a
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
ls -l /usr/bin/python*

ln -sf /usr/bin/python3.9 /usr/bin/python3
ln -sf /usr/bin/python3.9 /usr/bin/python

update-alternatives --install /usr/bin/python python /usr/bin/python3 python -V # python 3.9.5
```

```
apt update
apt upgrade
apt install libopencv-dev
# pip install "ruamel.yaml<0.18.0" numpy==1.26.4 tensorboard==2.18.0
pip install uv
export UV_SYSTEM_PYTHON=1
uv pip install torch torchvision torchaudio 
uv pip install "ruamel.yaml<0.18" "numpy<2" tensorboard pygame matplotlib mplcursors

# if you have cuda error
uv pip install --system --reinstall torch --index-url https://download.pytorch.org/whl/cu128
```

if you only have raisim2Lib, and have setup.py error
```
mkdir -p /raisim_ws/raisimLib/thirdParty
git clone -b v2.10.4 --depth 1 https://github.com/pybind/pybind11.git \
  /raisim_ws/raisimLib/thirdParty/pybind11

rm -rf build raisimGymForSegway.egg-info
python setup.py develop --CMAKE_PREFIX_PATH /raisim_ws/raisim2Lib/raisim
```

- add raisim activation key
```
git clone git@github.com:KyeongminNam/RAILAB_setting.git
mkdir /root/.raisim
cp RAILAB_setting/activation.raisim /root/.raisim/
```


- Some useful commands
```
git clone git@github.com:KyeongminNam/raisimGymForSegway.git
python setup.py develop --CMAKE_PREFIX_PATH ../raisimLib/raisim/linux
python setup.py develop --CMAKE_PREFIX_PATH ../raisim2Lib/raisim/linux
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

#### 2) failed fo create task for container
- Error message :
```
nkm@user-desktop:~$ docker start nkm
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/tmp/.docker.xauth" to rootfs at "/tmp/.docker.xauth": create mountpoint for /tmp/.docker.xauth mount: cannot create subdirectories in "/var/lib/docker/overlay2/7faa27964b2a3673c74238eaf6cbbb60ce73fc7b99b46cfc39ebe307ac19e1cb/merged/tmp/.docker.xauth": not a directory: unknown: Are you trying to mount a directory onto a file (or vice-versa)? Check if the specified host path exists and is the expected type
Error: failed to start containers: nkm
```

When you try
```
ls -ld /tmp/.docker.xauth
file /tmp/.docker.xauth
```
then it will say `/tmp/.docker.xauth: directory`. It should be file, but is a directory. Then try :

```
sudo rm -rf /tmp/.docker.xauth
touch /tmp/.docker.xauth
chmod 644 /tmp/.docker.xauth
```