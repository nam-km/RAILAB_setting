# Linux Setting Manual (Ubuntu 22.04)
Last Updated : 2026.11.05

Set up a desktop PC on **Ubuntu 22.04** for raisim2, raisin, RL training, and flashing the Jetson.
The Jetson needs a 22.04 host: NVIDIA's JetPack 7.2 supports 22.04/24.04 hosts and the CTI BSP supports 20.04/22.04 (see `robot_setting/Jetson_setting_ubuntu24.md`).

| Item | Version |
|---|---|
| OS | Ubuntu 22.04 |
| NVIDIA driver | 580 (open kernel module) |
| CUDA | 13.0 |
| cuDNN | 9 (`cudnn9-cuda-13`) |
| PyTorch | 2.14 (cu130) |
| Python | 3.12 (miniconda) |
| CLion | latest (2026.2, snap) |

- CUDA 13.0 because PyTorch 2.14 ships cu126 / cu130 / cu132 wheels (cu130 is the default) and no longer builds cu128.
- CUDA 13 needs an RTX 20 series (Turing) or newer GPU.

This manual has only the 22.04-specific steps (3–9). The steps that are the same on every Ubuntu version are in `desktop_setting.md`: backup, Korean input, basic tools, GitHub, Claude Code, Terminator, Miniconda, apps, launchers, `~/.bashrc`. Follow the order at the top of `desktop_setting.md`.

----
## 0–2. Backup, Ubuntu, basic tools
In `desktop_setting.md`, sections 0–4.

----
## 3. NVIDIA driver
```
sudo apt install -y nvidia-driver-580-open
sudo reboot
```
- `-open` is the open kernel module: NVIDIA recommends it for RTX 20 series and newer, and RTX 50 series requires it.
- If Secure Boot is on, the install asks for a password. After the reboot, pick **Enroll MOK** on the blue screen and enter that password, or the driver won't load.
- Check: `nvidia-smi` shows the GPU and `CUDA Version: 13.x`.

----
## 4. CUDA 13.0 + cuDNN 9
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo tee /etc/apt/preferences.d/nvidia-driver-from-ubuntu > /dev/null <<'EOF'
Package: nvidia-* libnvidia-* xserver-xorg-video-nvidia-*
Pin: origin "developer.download.nvidia.com"
Pin-Priority: -1
EOF
sudo apt update
sudo apt install -y cuda-toolkit-13-0 cudnn9-cuda-13
```
- The pin file keeps the driver from step 3. NVIDIA's repo has a newer `nvidia-driver-580-open` build, and without the pin `apt upgrade` switches to it. The toolkit and cuDNN don't depend on any driver package.
- Install `cuda-toolkit-13-0`, not `cuda` or `cuda-13-0`: those also install NVIDIA's driver and replace the one from step 3.
- The CUDA `PATH` and `LD_LIBRARY_PATH` lines are the first two lines of the `~/.bashrc` block in `desktop_setting.md` section 9.
- Check (in a new terminal, after adding the `~/.bashrc` lines): `nvcc --version` (13.0) and `dpkg -l | grep cudnn9` (9.x).

----
## 5. conda env + PyTorch
Miniconda itself is in `desktop_setting.md` section 4.
```
conda create -n raisim python=3.12
conda activate raisim
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
pip install numpy scipy matplotlib tensorboard wandb onnx onnxruntime "ruamel.yaml<0.18"
```
- `ruamel.yaml<0.18`: see `desktop_setting.md` section 4.
- PyTorch wheels bundle their own CUDA runtime and cuDNN, so torch works even before step 4. Step 4 is for compiling CUDA code.
- Check:
```
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
- wandb login: `desktop_setting.md` section 4.

----
## 6. raisin
Your GitHub account needs access to `railabatkaist/raisin_master` and `nam-km/raisin` (private). `install_dependencies.sh` asks y/n once.
Run it with no conda env active (`conda deactivate`): it pip-installs packages for the system Python.
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
- Not checked on 22.04 with the current `raisin_master`. On 24.04, `raisin_master` `66edc92` with `nam-km/raisin` `d820ecb7` needed fixes that don't depend on the Ubuntu version: `python3 raisin.py setup` instead of `raisin_workspace_setup.py`, the `raisin_workspace_setup.py → raisin.py` link, the `time.cpp` return line, the libtorch `.zip.html` rename, and the extra repos `raisin_plugin` / `raiway_controller`. See `Linux_setting_24.md` step 6.

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
## 9. Jetson flashing host
- Install sdkmanager: https://developer.nvidia.com/sdk-manager
```
sudo apt install ./sdkmanager_*_amd64.deb
```
- Flashing steps: `robot_setting/Jetson_setting_ubuntu24.md`, Step 1.

----
## 10. ~/.bashrc
In `desktop_setting.md` section 9 (CUDA lines, aliases for raisim, raisin and the lab servers). Drop the `-DSPHINX_EXECUTABLE` option from `build` / `cleanbuild` unless you made the docs venv from `Linux_setting_24.md` step 6.
