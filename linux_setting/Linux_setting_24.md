# Linux Setting Manual (Ubuntu 24.04)
Last Updated : 2026.11.05

Set up a desktop PC on **Ubuntu 24.04** for raisim2, raisin, and RL training.
This PC can't flash the Jetson: the CTI flash tools need a 20.04/22.04 host (see `robot_setting/Jetson_setting_ubuntu24.md`, Step 0). Use a 22.04 PC (`Linux_setting_22.md`) for that.

This manual has only the 24.04-specific steps (3–9). The steps that are the same on every Ubuntu version are in `desktop_setting.md`: backup, Korean input, basic tools, GitHub, Claude Code, Terminator, Miniconda, apps, launchers, `~/.bashrc`. Follow the order at the top of `desktop_setting.md`.

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
## 0–2. Backup, Ubuntu, basic tools
In `desktop_setting.md`, sections 0–4.

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
- The CUDA `PATH` and `LD_LIBRARY_PATH` lines are the first two lines of the `~/.bashrc` block in `desktop_setting.md` section 9.
- Check (in a new terminal, after adding the `~/.bashrc` lines): `nvcc --version` (13.2) and `dpkg -l | grep cudnn9` (9.x).

----
## 5. conda env + PyTorch
Miniconda itself is in `desktop_setting.md` section 4.
```
conda create -n raisim python=3.12
conda activate raisim
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu132
pip install numpy scipy matplotlib tensorboard wandb onnx onnxruntime "ruamel.yaml<0.18"
```
- Python 3.12 matches the system Python of 24.04 (PyTorch 2.15 supports 3.11 to 3.15).
- `ruamel.yaml<0.18`: see `desktop_setting.md` section 4.
- The torch download is about 3–4 GB (torch plus the `nvidia-*` CUDA libraries).
- PyTorch wheels bundle their own CUDA runtime and cuDNN, so torch works even before step 4. Step 4 is for compiling CUDA code.
- Check:
```
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
- wandb login: `desktop_setting.md` section 4.

----
## 6. raisin
Your GitHub account needs access to `railabatkaist/raisin_master`, `nam-km/raisin`, `nam-km/raisin_plugin` and `nam-km/raiway_controller` (private).

| Repo | Branch | Path |
|---|---|---|
| `railabatkaist/raisin_master` | default | `~/raisin_network_ws` |
| `nam-km/raisin` | `raiway_network` | `src/raisin` |
| `nam-km/raisin_plugin` | `raiway_network` | `src/raisin_plugin` |
| `nam-km/raiway_controller` | `master` | `src/raiway_controller` |

Dependencies:
```
sudo apt install -y libminizip-dev libavdevice-dev \
  python3-numpy python3-scipy python3-pandas python3-sklearn python3-networkx \
  python3-geopandas python3-fiona python3-pyproj python3-shapely \
  python3-sphinx python3-breathe python3-sphinx-rtd-theme \
  python3-venv texlive-font-utils

mkdir ~/raisin_network_ws && cd ~/raisin_network_ws
git clone git@github.com:railabatkaist/raisin_master.git .
git clone -b raiway_network git@github.com:nam-km/raisin.git src/raisin
git clone -b raiway_network git@github.com:nam-km/raisin_plugin.git src/raisin_plugin
git clone -b master git@github.com:nam-km/raiway_controller.git src/raiway_controller

conda deactivate
./src/raisin/install_dependencies.sh
```
- `src/raisin/install_dependencies.sh` asks y/n once. Check that it prints `/usr/bin/python3`, not a conda Python. On 24.04 it installs the Python packages with apt (`python3-osmnx`, `python3-numpy`, ...), not pip.
- Don't run the `install_dependencies.sh` at the workspace root. It installs pre-commit with `sudo pip install --break-system-packages`, and fails unless `raisin.py` has run first.
- `texlive-font-utils` gives `epstopdf`. Without it the docs build prints `epstopdf: not found`, which is harmless.

Sphinx extensions for the docs build. The docs need `sphinx_tabs`, `sphinx_panels` and `sphinxcontrib.youtube`. `sphinxcontrib-youtube` isn't in the 24.04 apt repo, so install the three in a venv that also sees the apt Sphinx:
```
python3 -m venv --system-site-packages ~/.venvs/raisin-docs
~/.venvs/raisin-docs/bin/pip install sphinx-tabs sphinx-panels sphinxcontrib-youtube
cat > ~/.venvs/raisin-docs/bin/sphinx-build <<'EOF'
#!/bin/sh
# System Sphinx + extensions pip-installed in this venv
exec "$(dirname "$0")/python" -m sphinx "$@"
EOF
chmod +x ~/.venvs/raisin-docs/bin/sphinx-build
```
- The venv has no `sphinx-build` of its own, because Sphinx comes from apt. The wrapper runs Sphinx with the venv's Python.
- Pass it to cmake with `-DSPHINX_EXECUTABLE` (below and in the `build` / `cleanbuild` aliases in `desktop_setting.md` section 9). Without it, cmake picks `/usr/bin/sphinx-build` and the build stops at `Could not import extension sphinx_tabs.tabs`.

Fixes needed with these commits (`raisin_master` `66edc92`, `nam-km/raisin` `d820ecb7`):
```
cd ~/raisin_network_ws
ln -s raisin.py raisin_workspace_setup.py
```
- `raisin_master` renamed `raisin_workspace_setup.py` to `raisin.py`, but `raisin_util` in `nam-km/raisin` still looks for `raisin_workspace_setup.py` to find the workspace. Without the link, `raisin_gui` and the nodes print `[Raisin Util] install directory is ` (empty), then `Could not find file: params.yaml` and abort. The link also keeps the `cleanbuild` alias working. `railabatkaist/raisin` already looks for `raisin.py`.
- `raisin_tf/src/time.cpp`: the body of `tf2::displayTimePoint()` is commented out, so it has no `return` and `-Werror=return-type` stops the build. Add this line before its closing `}`:
```
  return std::to_string(tf2::timeToSec(stamp));
```

Build:
```
cd ~/raisin_network_ws
echo raisin_rf > RAISIN_IGNORE
python3 raisin.py setup
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DSPHINX_EXECUTABLE=$HOME/.venvs/raisin-docs/bin/sphinx-build
```
- If cmake stops at `Failed to open .../libtorch-cxx11-abi-shared-with-deps-1.10.2+cpu.zip`: `raisin_torch` downloads libtorch with `wget -E`, which saves it as `.zip.html`. Rename it and run cmake again. It's only needed the first time, because it is extracted into `src/raisin/raisin_torch/pytorch/`.
```
mv libtorch-cxx11-abi-shared-with-deps-1.10.2+cpu.zip.html libtorch-cxx11-abi-shared-with-deps-1.10.2+cpu.zip
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DSPHINX_EXECUTABLE=$HOME/.venvs/raisin-docs/bin/sphinx-build
```
```
ninja -j $(nproc)
```
- Check: the `tester` alias (`desktop_setting.md` section 9) opens the raisin GUI and the raiway node. The GUI log shows `Detected peer: railab_raiway-...`.

----
## 7. raisim
Build dependencies (raisim and raisim2 both need Eigen3, and rayrai needs SDL2):
```
sudo apt install -y libeigen3-dev libsdl2-dev
```
- Step 6 (`install_dependencies.sh`) may already install these, but without them cmake stops with `Could not find a package configuration file provided by "Eigen3"` if you do this step first.

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
Flash from a 22.04 PC: `Linux_setting_22.md` step 9 and `robot_setting/Jetson_setting_ubuntu24.md`.

----
## 10. ~/.bashrc
In `desktop_setting.md` section 9 (CUDA lines, aliases for raisim, raisin and the lab servers).
