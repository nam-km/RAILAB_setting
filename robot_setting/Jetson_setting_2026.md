# Jetson Setting Manual
Last Updated : 2026.10.26

How to set up a new robot PC (Ubuntu 24.04) from an empty board, matching the 2025 robot PC.

| Item | Version |
|---|---|
| Board | CTI Rogue-Orin (AGX202) + Jetson AGX Orin |
| BSP | CTI-L4T ORIN-AGX 39.2.0 (Jetson Linux 39.2, kernel 6.8) |
| JetPack | 7.2 (CUDA 13, cuDNN 9, TensorRT 10) |
| OS | Ubuntu 24.04 |
| Root disk | NVMe SSD |
| User / hostname | `raiway` / `raiway` |

Files used by this manual are in `robot_setting/files/` of this repo.

----
## Step 0: Host PC
- The host PC must be **Ubuntu 22.04 or 20.04** (the CTI flash tools don't support 24.04 on the host).
- Install sdkmanager: https://developer.nvidia.com/sdk-manager
```
sudo apt install ./sdkmanager_*_amd64.deb
```

----
## Step 1: Flash CTI-L4T
The Rogue carrier board needs Connect Tech's BSP (drivers and device tree) on top of NVIDIA's Jetson Linux, or its ports won't work.

Guide: https://connecttech.com/resource-center/kdb373/
1. In sdkmanager, choose **JetPack 7.2** / AGX Orin and **uncheck "Jetson SDK components"**. Skip the 2 pop-ups to download Jetson Linux only.
2. Download the BSP `CTI-L4T-ORIN-AGX-39.2.0-V00X.tgz` (latest V00X): https://connecttech.com/resource-center/l4t-board-support-packages/
   - Release notes: https://connecttech.com/ftp/Drivers/L4T-Release-Notes/Jetson-AGX-Orin/ORIN-AGX-39.2.0.pdf
3. Put it in `~/nvidia/nvidia_sdk/JetPack_7.2_Linux_JETSON_AGX_ORIN_TARGETS/Linux_for_Tegra`, then:
```
tar -xzvf CTI-L4T-ORIN-AGX-39.2.0-V00X.tgz
cd CTI-L4T && sudo ./install.sh && cd ..
```
4. Put the Jetson in recovery mode, connect it to the host by USB (`lsusb` shows `NVIDIA Corp.`), then:
```
sudo ./cti-flash.sh      # rogue-orin -> base -> orin-agx
```
   - Flash straight to the **NVMe SSD**: the onboard eMMC is only 64 GB. The old `rootOnNVMe` script doesn't work on JetPack 6 or later. The release notes above explain how to choose NVMe as the target.
5. On the Jetson screen, finish the Ubuntu setup (user `raiway`, hostname `raiway`).
6. Check: `lsblk` shows `nvme0n1p1` mounted on `/`.

----
## Step 2: JetPack SDK components
CUDA, cuDNN, TensorRT, VPI, Nsight, and NVIDIA's Docker runtime.

Guide: https://connecttech.com/resource-center/kdb374/
- In sdkmanager, select everything **except** Jetson Linux, then enter the Jetson's username and password.
- Or, on the Jetson itself: `sudo apt update && sudo apt install nvidia-jetpack`
- Add to `~/.bashrc` (lets you run `nvcc` and lets programs find the CUDA libraries):
```
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```
- Check: `nvcc --version`

----
## Step 3: Basic tools
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential ninja-build curl nano vim terminator \
  openssh-server python3-pip python-is-python3 docker.io \
  htop net-tools ethtool iperf3 can-utils ffmpeg plocate
sudo snap install yq
```
| Tool | Why |
|---|---|
| terminator | split-screen terminal |
| openssh-server | log in to the robot from a laptop |
| ninja-build | the raisin build uses Ninja |
| python-is-python3 | makes `python` mean `python3` |
| docker.io | run containers (NVIDIA runtime comes with JetPack) |
| htop, net-tools, ethtool, iperf3 | check CPU and network |
| can-utils | CAN bus debugging |
| yq | read/edit YAML files from the shell |

- VS Code (arm64 .deb from https://code.visualstudio.com/download). It also adds Microsoft's apt repo, so `apt upgrade` keeps it updated.
```
sudo apt install ./code_*_arm64.deb
```
- mcfly: replaces Ctrl+R with a smarter shell history search. Download `mcfly-*-aarch64-unknown-linux-gnu.tar.gz` from https://github.com/cantino/mcfly/releases
```
tar -xzf mcfly-*-aarch64-unknown-linux-gnu.tar.gz
sudo mv mcfly /usr/local/bin/
echo 'eval "$(mcfly init bash)"' >> ~/.bashrc
```
- Git and SSH key: needed to clone the private GitHub repos. Add `id_ed25519.pub` to GitHub.
```
git config --global user.name "<name>"
git config --global user.email "<email>"
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```
- Password-free SSH from your laptop: on the laptop, run
```
ssh-copy-id raiway@<robot IP>
```
- User groups: `dialout` lets you open serial ports (`/dev/ttyACM0`) without sudo, and `docker` lets you run docker without sudo. Log out and back in afterwards.
```
sudo usermod -aG dialout,docker $USER
```
- Handy `~/.bashrc` aliases:
```
alias gb="gedit ~/.bashrc"
alias sb="source ~/.bashrc"
```

----
## Step 4: Libraries
Most raisin dependencies are installed in Step 10 by raisin's own script. These are the extras:
```
sudo apt install -y libzstd-dev libusb-1.0-0-dev libpcap-dev \
  gdal-bin libgdal-dev python3-gdal python3-fiona python3-matplotlib python3-scipy python3-pandas
```
- GDAL/fiona are for map (GIS) data in the GUI. The apt GDAL on 24.04 is 3.8, so you no longer need the 2025 source builds of GDAL and VTK.
- Optional, to build the raisin docs:
```
sudo apt install -y doxygen python3-sphinx python3-breathe python3-sphinx-rtd-theme
```
- Add to `~/.bashrc` (lets programs find libraries installed to `/usr/local`, e.g. by raisim):
```
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
```

----
## Step 5: RealSense SDK
For the Intel RealSense cameras. On Jetson, build from source with the RSUSB backend, because the kernel-patch (dkms) packages don't support the Jetson kernel.

**Unplug all RealSense cameras while installing.**
```
cd ~ && git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
./scripts/setup_udev_rules.sh        # lets normal users open the camera
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DFORCE_RSUSB_BACKEND=ON -DBUILD_WITH_CUDA=ON -DBUILD_EXAMPLES=ON
make -j8 && sudo make install
```
- Check: plug in the camera and run `realsense-viewer`.

----
## Step 6: raisim
Physics engine used by raisin for simulation and robot models.
```
mkdir ~/raisim_ws && cd ~/raisim_ws
git clone git@github.com:raisimTech/raisimLib.git
cd raisimLib && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j8
```
- License: copy `activation.raisim` from this repo to `~/.raisim/activation.raisim`.
- raisimUnreal (the visualizer from raisim's GitHub releases) only runs on x86 PCs, so run it on a desktop instead of the Jetson.

----
## Step 7: EtherCAT LAN card (Realtek RTL8125)
The motor drivers are on EtherCAT through the RTL8125 card. Realtek's own driver is more stable than the kernel's built-in one.
1. Check the card: `lspci | grep Ethernet` shows 2× `RTL8125 2.5GbE Controller`.
2. Download the **latest** r8125 driver (must support kernel 6.8) from https://www.realtek.com/Download/List?cate_id=584
```
tar -xvf r8125-*.tar.bz2
cd r8125-*/
sudo ./autorun.sh     # must print "Completed"
sudo reboot
```
3. Give the EtherCAT port a fixed name, `ethercat`, so that code and aliases always find it. Find its MAC with `ip -br link`, then write `/etc/udev/rules.d/99-ethercat.rules`:
```
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="<MAC>", NAME="ethercat"
```
Reboot. Check: `ip -br link` shows `ethercat`.

----
## Step 8: SOEM (EtherCAT test tool)
Use it to check that every motor driver answers on the EtherCAT bus.
```
cd ~ && git clone https://github.com/OpenEtherCATsociety/SOEM.git
cd SOEM && mkdir build && cd build
cmake .. && make
```
- Add to `~/.bashrc`:
```
alias slaveinfo="sudo ~/SOEM/build/test/linux/slaveinfo/slaveinfo ethercat"
alias simpletest="sudo ~/SOEM/build/test/linux/simple_test/simple_test ethercat"
```
- Check: `slaveinfo` lists the motor drivers.

----
## Step 9: Wi-Fi hotspot (create_ap)
The robot creates its own Wi-Fi called `raiway`, so a laptop or joystick can connect without a router.
```
sudo apt install -y hostapd iw haveged dnsmasq
cd ~ && git clone https://github.com/oblique/create_ap.git
cd create_ap && sudo make install
```
- Stop NetworkManager from controlling `wlan0` (otherwise it fights with create_ap). Add this to `/etc/NetworkManager/NetworkManager.conf`:
```
[keyfile]
unmanaged-devices=interface-name:wlan0
```
- `~/create_ap/make_ap.py`: first makes the serial device `/dev/ttyACM0` readable by everyone, then starts the hotspot (SSID `raiway`, password `00000000`, 2.4 GHz channel 6):
```
import os
os.system("sudo chmod 666 /dev/ttyACM0")
os.system("sudo create_ap -n wlan0 'raiway' '00000000' --freq-band 2.4 --no-virt -w 2 -c 6 --ieee80211n")
```
- `/etc/systemd/system/raiway_create_ap.service` starts the hotspot at boot and restarts it if it crashes:
```
[Unit]
Description=Create AP Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/raiway/create_ap/make_ap.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl restart NetworkManager
sudo systemctl daemon-reload
sudo systemctl enable --now raiway_create_ap.service
```
Check: the Wi-Fi `raiway` appears. With `-n`, there's no internet sharing, so use the wired port (`eth0`) for internet.

----
## Step 10: raisin (network) workspace
raisin is the robot control software. `raisin_master` is the workspace, and the robot code goes in `src/`.
```
mkdir ~/raisin_network_ws && cd ~/raisin_network_ws
git clone git@github.com:railabatkaist/raisin_master.git .
cd src
git clone -b raiway_network git@github.com:nam-km/raisinForRaiway.git raisin
git clone -b raiway_network git@github.com:nam-km/raisin_plugin.git
git clone -b ral_submission git@github.com:nam-km/raiway_controller.git
```
- Install raisin's dependencies (it supports 24.04 and asks y/n once):
```
cd ~/raisin_network_ws/src/raisin
./install_dependencies.sh
```
- Copy 2 local files from this repo's `robot_setting/files/` to `~/raisin_network_ws/` (they aren't in git):
  - `RAISIN_IGNORE`: the packages to skip when building (simulation-only and unused plugins).
  - `modify_cmakelists.sh`: adds the Boost path to `CMakeLists.txt`, which the aarch64 build needs.
- Copy the robot config from `robot_setting/files/raisin/` to `~/.raisin/`:
  - `homing.conf`: the robot's joint homing (zero position) values. **Only valid for this robot.** Redo homing if the robot is different.
  - `raisin_gui/params.yaml`: the GUI talks to the robot over `wlan0`.
- First build:
```
cd ~/raisin_network_ws
python3 raisin_workspace_setup.py     # generates message code and CMake files
./modify_cmakelists.sh
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64
ninja -j 8
```
- `/etc/systemd/system/raisin_raiway_node.service` starts the robot node at boot as root (EtherCAT needs raw network access) and restarts it 2 s after any crash:
```
[Unit]
Description=raisin raiway node
After=network.target

[Service]
Type=simple
ExecStart=/home/raiway/raisin_network_ws/install/scripts/raisin_raiway/scripts/raisin_service.sh
Restart=always
RestartSec=2
User=root
Group=root

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl enable --now raisin_raiway_node.service
```
- Add to `~/.bashrc`:
```
# rebuild and restart the node
alias build="cd ~/raisin_network_ws/build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64 && ninja -j 8 && sudo systemctl restart raisin_raiway_node.service"
# regenerate everything and rebuild from scratch
alias cleanbuild="cd ~/raisin_network_ws && python3 raisin_workspace_setup.py && ./modify_cmakelists.sh && rm -rf build && mkdir build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64 && ninja -j 8 && sudo systemctl restart raisin_raiway_node.service"
alias gui="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_gui/raisin_gui/raisin_gui"
# run the node by hand (stop the service first): simulation / real robot
alias node="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_raiway/raisin_raiway_node"
alias realnode="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_raiway/raisin_raiway_node real"
```

----
## Useful commands
```
sudo systemctl status raisin_raiway_node.service     # node status
sudo systemctl stop raisin_raiway_node.service       # stop node (before running it by hand)
journalctl -u raisin_raiway_node.service -f          # node log
sudo systemctl restart raiway_create_ap.service      # restart hotspot
```
