# Linux Setting Manual (Ubuntu 24.04)
Last Updated : 2026.11.02

Set up a desktop PC on **Ubuntu 24.04** for raisim2, raisin, and RL training.
This PC can't flash the Jetson: the CTI flash tools need a 20.04/22.04 host (see `robot_setting/Jetson_setting_2026.md`, Step 0). Use a 22.04 PC (`Linux_setting_22.md`) for that.

| Item | Version |
|---|---|
| OS | Ubuntu 24.04 |
| NVIDIA driver | 595 (open kernel module) |
| CUDA | 13.2 |
| cuDNN | 9 (`cudnn9-cuda-13`) |
| PyTorch | 2.15 (cu132) |
| Python | 3.12 (miniconda) |
| CLion | latest (snap) |

- CUDA 13.2 because PyTorch 2.15 ships cu132 (default) / cu134 wheels and no longer builds cu126 or cu130.
- Driver 595 is the R595 branch that CUDA 13.2 was released with. Any driver >= 580 runs CUDA 13.x (minor version compatibility), so 580 also works if 595 isn't offered for your GPU.
- CUDA 13 needs an RTX 20 series (Turing) or newer GPU. Driver 590 and newer also dropped the GTX 10 series.
- If you need PyTorch 2.14 (cu130) for an older project: `pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu130` works with the same driver.

----
## 0. Before reinstalling
If you are reinstalling an existing PC, copy these to an external disk first:
- `~/.ssh/`, `~/.bashrc`, `~/.raisim/`
- Uncommitted or unpushed work: run `git status` in each repo under `~/raisim_ws` and `~/raisin_network_ws/src`
- Training logs and data

----
## 1. Ubuntu
- Install Ubuntu 24.04 Desktop.
- Korean input:
  1. Settings → System → Region & Language → Manage Installed Languages → Install / Remove Languages → check **Korean**.
  2. `sudo apt install -y ibus-hangul`, then log out and back in.
  3. Settings → Keyboard → Input Sources → **+** → Korean → **Korean (Hangul)**. Switch with Shift+Space (change it in the Hangul preferences).

----
## 2. Basic tools
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential ninja-build curl wget vim terminator tmux \
  openssh-server python3-pip python-is-python3 htop gpustat net-tools jq ffmpeg imagemagick
```
- VS Code: https://code.visualstudio.com/download → `sudo apt install ./code_*_amd64.deb`
- Chrome: https://www.google.com/chrome/ → `sudo apt install ./google-chrome-stable_current_amd64.deb`
- mcfly (better Ctrl+R): https://github.com/cantino/mcfly/releases → `mcfly-*-x86_64-unknown-linux-musl.tar.gz`
```
tar -xzf mcfly-*.tar.gz && sudo mv mcfly /usr/local/bin/
```
- Claude Code:
```
curl -fsSL https://claude.ai/install.sh | bash
```
- Codex:
```
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```
- GitHub SSH key (add the `.pub` to GitHub):
```
git config --global user.email twinhk@kaist.ac.kr
git config --global user.name KyungminNam
ssh-keygen -t ed25519 && cat ~/.ssh/id_ed25519.pub
```
- On 24.04, `pip install` into the system Python is refused (`externally-managed-environment`). Use the conda env from step 5 for Python packages; don't use `--break-system-packages`.

----
## 3. NVIDIA driver
```
sudo apt install -y nvidia-driver-595-open
sudo reboot
```
- `-open` is the open kernel module: NVIDIA recommends it for RTX 20 series and newer, and RTX 50 series requires it.
- `ubuntu-drivers devices` lists the drivers Ubuntu offers for your GPU. If 595 isn't there, `nvidia-driver-580-open` also runs CUDA 13.2.
- If Secure Boot is on, the install asks for a password. After the reboot, pick **Enroll MOK** on the blue screen and enter that password, or the driver won't load.
- Check: `nvidia-smi` shows the GPU and `CUDA Version: 13.x`.

----
## 4. CUDA 13.2 + cuDNN 9
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo tee /etc/apt/preferences.d/nvidia-driver-from-ubuntu > /dev/null <<'EOF'
Package: nvidia-* libnvidia-* xserver-xorg-video-nvidia-*
Pin: origin "developer.download.nvidia.com"
Pin-Priority: -1
EOF
sudo apt update
sudo apt install -y cuda-toolkit-13-2 cudnn9-cuda-13
```
- The pin file keeps the driver from step 3. NVIDIA's repo ships its own driver packages, and without the pin `apt upgrade` can switch to them. The toolkit and cuDNN don't depend on any driver package.
- Install `cuda-toolkit-13-2`, not `cuda` or `cuda-13-2`: those also install NVIDIA's driver and replace the one from step 3.
- Add to `~/.bashrc`:
```
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```
- Check: `nvcc --version` (13.2) and `dpkg -l | grep cudnn9` (9.x).

----
## 5. Python (miniconda) + PyTorch
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh        # answer yes to conda init
source ~/.bashrc
conda config --set auto_activate_base false

conda create -n raisim python=3.12            # accept the Anaconda Terms of Service if asked
conda activate raisim
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu132
pip install numpy scipy matplotlib tensorboard wandb onnx onnxruntime "ruamel.yaml<0.18"
```
- Python 3.12 matches the system Python of 24.04 (PyTorch 2.15 supports 3.11 to 3.15).
- `ruamel.yaml<0.18`: raisimGym imports `ruamel.yaml.dump`, which 0.18 removed.
- PyTorch wheels bundle their own CUDA runtime and cuDNN, so torch works even before step 4. Step 4 is for compiling CUDA code.
- Check:
```
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
- wandb: make an account at https://wandb.ai/site, then `wandb login` and paste the key from https://wandb.ai/authorize.

----
## 6. raisin
Your GitHub account needs access to `railabatkaist/raisin_master` and `nam-km/raisin` (private). `install_dependencies.sh` asks y/n once.
Run it with no conda env active (`conda deactivate`). On 24.04 it installs the Python packages with apt (`python3-osmnx`, `python3-numpy`, ...), not pip.
```
sudo apt install -y libminizip-dev libavdevice-dev \
  python3-numpy python3-scipy python3-pandas python3-sklearn python3-networkx \
  python3-geopandas python3-fiona python3-pyproj python3-shapely \
  python3-sphinx python3-breathe python3-sphinx-rtd-theme

mkdir ~/raisin_network_ws && cd ~/raisin_network_ws
git clone git@github.com:railabatkaist/raisin_master.git .
git clone -b raiway_network git@github.com:nam-km/raisin.git src/raisin
./src/raisin/install_dependencies.sh
echo raisin_rf > RAISIN_IGNORE
python3 raisin_workspace_setup.py
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j $(nproc)
```

----
## 7. raisim
Activation key (same key as `activation.raisim` in this repo):
```
mkdir -p ~/.raisim && cp activation.raisim ~/.raisim/
```
raisim2:
```
mkdir -p ~/raisim_ws && cd ~/raisim_ws
git clone git@github.com:raisimTech/raisim2Lib.git
cd raisim2Lib && source ./raisim_env.sh
cmake -S . -B build-examples -DCMAKE_BUILD_TYPE=Release -DRAISIM_EXAMPLE=ON
cmake --build build-examples --parallel $(nproc)
```
- Check: `./build-examples/examples/rayrai_tcp_viewer`, then `./build-examples/examples/primitive_grid` in another terminal (both after `source ./raisim_env.sh`).

raisim (v1, for older raisimGym projects):
```
cd ~/raisim_ws
git clone git@github.com:raisimTech/raisimLib.git
cd raisimLib && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j $(nproc)
chmod +x ../raisimUnity/linux/raisimUnity.x86_64
```

----
## 8. CLion
```
sudo snap install clion --classic
```
- CMake options (Settings → Build, Execution, Deployment → CMake), use the full path:
  - raisim2: `-DCMAKE_PREFIX_PATH=/home/<user>/raisim_ws/raisim2Lib/raisim`
  - raisim v1: `-DCMAKE_PREFIX_PATH=/home/<user>/raisim_ws/raisimLib/raisim/linux`

----
## 9. Jetson flashing
Not from this PC. sdkmanager runs on 24.04, but the CTI BSP flash script (`cti-flash.sh`) only supports 20.04/22.04 hosts.
Flash from a 22.04 PC: `Linux_setting_22.md` step 9 and `robot_setting/Jetson_setting_2026.md`.

----
## 10. ~/.bashrc
```
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
export raisim_DIR=$HOME/raisim_ws/raisimLib/raisim/linux
eval "$(mcfly init bash)"

alias gb="gedit ~/.bashrc"
alias sb="source ~/.bashrc"
alias car="conda activate raisim"

# raisim
alias ru="cd ~/raisim_ws/raisimLib/raisimUnity/linux && ./raisimUnity.x86_64"
alias ru2="cd ~/raisim_ws/raisim2Lib && source ./raisim_env.sh && ./build-examples/examples/rayrai_tcp_viewer"
alias unreal="cd ~/Downloads/Linux/ && bash raisimUnreal2.sh"

# raisin
alias build="cd ~/raisin_network_ws/build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j $(nproc)"
alias cleanbuild="cd ~/raisin_network_ws && rm -rf generated/ build/ install/ CMakeLists.txt && python3 raisin_workspace_setup.py && mkdir build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j $(nproc)"
alias gui="cd ~/raisin_network_ws && ./build/src/raisin/raisin_gui/raisin_gui/raisin_gui"
alias node2="cd ~/raisin_network_ws && ./build/src/raisin/raisin_raiway/raisin_raiway_node"
alias raibo2node="cd ~/raisin_network_ws && ./build/src/raisin/raisin_raibo2/raisin_raibo2_node"
alias tester="gui & node2"

# raisin_ws (ROS 2): needs ROS 2, which this manual doesn't install
alias cwbs="cd ~/raisin_ws/ && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release && source install/setup.bash"
alias cws="cd ~/raisin_ws/ && source install/setup.bash"

alias matlab='/usr/local/MATLAB/R2020a/bin/matlab -desktop'

# lab servers: ssh with port forwarding, cp* copies the server's ~/data to ~/
alias ssh101='ssh -L 4101:localhost:4101 nkm@143.248.6.101'
alias ssh1012='ssh -L 5101:localhost:5101 nkm@143.248.6.101'
alias cp101='cd ~ && scp -r nkm@143.248.6.101:data/ .'
alias ssh105='ssh -L 4444:localhost:4444 nkm@143.248.6.105'
alias ssh1052='ssh -L 5444:localhost:5444 nkm@143.248.6.105'
alias cp105='cd ~ && scp -r nkm@143.248.6.105:data/ .'
alias ssh83='ssh -L 4083:localhost:4083 nkm@143.248.6.83'
alias cp83='cd ~ && scp -r nkm@143.248.6.83:data/ .'
alias ssh189='ssh -L 4189:localhost:4189 nkm@143.248.247.189'
alias cp189='cd ~ && scp -r nkm@143.248.247.189:data/ .'
alias ssh168='ssh -L 4168:localhost:4168 nkm@143.248.6.168'
alias cp168='cd ~ && scp -r nkm@143.248.6.168:data/ .'
```

----
## Useful commands
Free the page cache (memory check):
```
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```
