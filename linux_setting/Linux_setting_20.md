### Basics
- Korean: https://freeablelab.tistory.com/138  
- vscode: download deb file in https://code.visualstudio.com/    
`sudo apt install ./code~~~`
- raisim: https://www.youtube.com/watch?v=oQjHMyDiay4&t=192s  
`export raisim_DIR=/home/nkm/raisim_ws/raisimLib/raisim/linux`  
`alias ru="cd /home/nkm/raisim_ws/raisimLib/raisimUnity/linux && ./raisimUnity.x86_64"`
```
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
make -j32

chmod +x ./raisimUnity.x86_64
```
- clion 21.3.4: https://www.jetbrains.com/clion/download/other.html, download tar.gz
```
sudo tar xvzf CLion-*.tar.gz -C /opt/
sh /opt/clion-*/bin/clion.sh
```
clion -> Tools -> Create Desktop Entry  
cmake options: -DCMAKE_PREFIX_PATH=/home/nkm/raisim_ws/raisimLib/raisim/linux

### Graphic driver install
https://donghyun99.tistory.com/18

### Cuda 11.7.1, Cudnn 8.9.7 on Ubuntu 20.04
https://velog.io/@qaszx1004/Install-CUDA11.8-CUDNN-on-Ubuntu-20.04
```
# write in ~/.bashrc and source
export PATH="/usr/local/cuda/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
```

Cuda : https://developer.nvidia.com/cuda-toolkit-archive  
Cudnn: https://developer.nvidia.com/rdp/cudnn-archive

```
cd /usr/local/cuda-11.7/lib64

sudo ln -sf libcudnn.so.8.9.7 libcudnn.so.8
sudo ln -sf libcudnn.so.8 libcudnn.so

sudo ln -sf libcudnn_adv_infer.so.8.9.7 libcudnn_adv_infer.so.8
sudo ln -sf libcudnn_adv_infer.so.8 libcudnn_adv_infer.so

sudo ln -sf libcudnn_adv_train.so.8.9.7 libcudnn_adv_train.so.8
sudo ln -sf libcudnn_adv_train.so.8 libcudnn_adv_train.so

sudo ln -sf libcudnn_cnn_infer.so.8.9.7 libcudnn_cnn_infer.so.8
sudo ln -sf libcudnn_cnn_infer.so.8 libcudnn_cnn_infer.so

sudo ln -sf libcudnn_cnn_train.so.8.9.7 libcudnn_cnn_train.so.8
sudo ln -sf libcudnn_cnn_train.so.8 libcudnn_cnn_train.so

sudo ln -sf libcudnn_ops_infer.so.8.9.7 libcudnn_ops_infer.so.8
sudo ln -sf libcudnn_ops_infer.so.8 libcudnn_ops_infer.so

sudo ln -sf libcudnn_ops_train.so.8.9.7 libcudnn_ops_train.so.8
sudo ln -sf libcudnn_ops_train.so.8 libcudnn_ops_train.so
```

check
```
nvidia-smi
nvcc -V
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2
```

### anaconda install (x. go miniconda)  
https://record-everything.tistory.com/entry/Ubuntu-2004-%EC%9A%B0%EB%B6%84%ED%88%AC%EC%97%90-%EC%95%84%EB%82%98%EC%BD%98%EB%8B%A4-%EC%84%A4%EC%B9%98-%EB%B0%8F-Python-%EA%B0%80%EC%83%81%ED%99%98%EA%B2%BD-%EC%84%A4%EC%A0%95

### miniconda install
https://docs.anaconda.com/free/miniconda/  
`sh Miniconda~~.sh`
```
./miniconda3/bin/conda init
source ~/.bashrc

conda config --set auto_activate_base false
conda create -n raisim python=3.9
conda activate raisim
```


### other dependency  
raisimGymForSegway: python 3.9.19, torch 2.0.1, tensorboard 2.18.0, numpy 1.26.4, numba 0.60.0
```
sudo apt install git-all
git config --global user.email twinhk@kaist.ac.kr
git config --global user.name KyungminNam

sudo apt install cmake minizip ffmpeg libeigen3-dev
sudo apt-get install python3-distutils

sudo apt-get install tmux
sudo apt-get install terminator
sudo apt-get install htop
sudo apt-get install gpustat
sudo apt-get install imagemagick
sudo apt-get install vim
sudo apt-get install python3-distutils


#conda raisim env setup
conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.7 -c pytorch -c nvidia

pip install numpy==1.26.4 tensorboard==2.18.0

pip install "ruamel.yaml<0.18.0"


```
pytorch: https://pytorch.org/get-started/locally/  
`python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`

### memory check
buffer cache delete : `sudo echo 3 > sudo /proc/sys/vm/drop_caches`

### wandb
make account : https://wandb.ai/site
```
pip install wandb
wandb login
# put key : https://wandb.ai/authorize
```
