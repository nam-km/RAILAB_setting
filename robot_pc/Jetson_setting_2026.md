# Jetson Setting Manual
Last Updated : 2026.10.26

How to set up a new robot PC (Ubuntu 24.04) from an empty board.

| Item | Version |
|---|---|
| Board | CTI Rogue-Orin (AGX202) + Jetson AGX Orin |
| BSP | CTI-L4T ORIN-AGX 39.2.0 (Jetson Linux 39.2, kernel 6.8) |
| JetPack | 7.2 (CUDA 13, cuDNN 9, TensorRT 10) |
| OS | Ubuntu 24.04 |
| Root disk | NVMe SSD |

----
## Step 0: Host PC
- The host PC must be **Ubuntu 22.04 or 20.04** (the CTI flash tools don't support 24.04 on the host).
- Install sdkmanager: https://developer.nvidia.com/sdk-manager
```
sudo apt install ./sdkmanager_*_amd64.deb
```

----
## Step 1: Flash CTI-L4T
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
   - Flash straight to the **NVMe SSD**. The old `rootOnNVMe` script doesn't work on JetPack 6 or later. The release notes above explain how to choose NVMe as the target.
5. On the Jetson screen, finish the Ubuntu setup (user: `raiway`).
6. Check: `lsblk` shows `nvme0n1p1` mounted on `/`.

----
## Step 2: JetPack SDK components
Guide: https://connecttech.com/resource-center/kdb374/
- In sdkmanager, select everything **except** Jetson Linux, then enter the Jetson's username and password.
- Or, on the Jetson itself: `sudo apt update && sudo apt install nvidia-jetpack`
- Add to `~/.bashrc`:
```
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```
- Check: `nvcc --version`

----
## Step 3: Basic tools
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential ninja-build curl nano terminator \
  openssh-server python3-pip python-is-python3 docker.io
```
- VS Code (arm64 .deb from https://code.visualstudio.com/download):
```
sudo apt install ./code_*_arm64.deb
```
- mcfly (shell history search): download `mcfly-*-aarch64-unknown-linux-gnu.tar.gz` from https://github.com/cantino/mcfly/releases
```
tar -xzf mcfly-*-aarch64-unknown-linux-gnu.tar.gz
sudo mv mcfly /usr/local/bin/
echo 'eval "$(mcfly init bash)"' >> ~/.bashrc
```
- Git SSH key (add `id_ed25519.pub` to GitHub):
```
git config --global user.name "<name>"
git config --global user.email "<email>"
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```
- User groups (serial port, docker):
```
sudo usermod -aG dialout,docker $USER
```

----
## Step 4: Libraries
```
sudo apt install -y libboost-all-dev libyaml-cpp-dev libpcl-dev libeigen3-dev libsdl2-dev \
  libopencv-dev python3-opencv libgeographiclib-dev libzstd-dev \
  gdal-bin libgdal-dev python3-gdal python3-fiona
```
- GDAL from apt is 3.8 on 24.04, so you don't need to build it from source anymore.
- On 24.04, pip refuses to install into the system Python unless you add `--break-system-packages`:
```
pip install --break-system-packages osmnx
pip install --break-system-packages breathe Sphinx sphinx-panels sphinx-rtd-theme sphinx-tabs
```
- Add to `~/.bashrc`:
```
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
```

----
## Step 5: raisim
```
mkdir ~/raisim_ws && cd ~/raisim_ws
git clone git@github.com:raisimTech/raisimLib.git
cd raisimLib && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j8
```
- Copy the license to `~/.raisim/activation.raisim` (there is a copy in this repo).

----
## Step 6: EtherCAT LAN card (Realtek RTL8125)
1. Check the card: `lspci | grep Ethernet`
2. Download the **latest** r8125 driver (must support kernel 6.8) from https://www.realtek.com/Download/List?cate_id=584
```
tar -xvf r8125-*.tar.bz2
cd r8125-*/
sudo ./autorun.sh     # must print "Completed"
sudo reboot
```
3. Rename the EtherCAT port to `ethercat`. Find its MAC with `ip -br link`, then write `/etc/udev/rules.d/99-ethercat.rules`:
```
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="<MAC>", NAME="ethercat"
```
Reboot. Check: `ip -br link` shows `ethercat`.

----
## Step 7: SOEM (EtherCAT test tool)
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
## Step 8: Wi-Fi hotspot (create_ap)
```
sudo apt install -y hostapd iw haveged
cd ~ && git clone https://github.com/oblique/create_ap.git
cd create_ap && sudo make install
```
- `~/create_ap/make_ap.py`:
```
import os
os.system("sudo chmod 666 /dev/ttyACM0")
os.system("sudo create_ap -n wlan0 'raiway' '00000000' --freq-band 2.4 --no-virt -w 2 -c 6 --ieee80211n")
```
- `/etc/systemd/system/raiway_create_ap.service`:
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
sudo systemctl daemon-reload
sudo systemctl enable --now raiway_create_ap.service
```
Check: the Wi-Fi `raiway` appears (password `00000000`).

----
## Step 9: raisin (network) workspace
```
mkdir ~/raisin_network_ws && cd ~/raisin_network_ws
git clone git@github.com:railabatkaist/raisin_master.git .
cd src
git clone -b raiway_network git@github.com:KyeongminNam/raisinForRaiway.git raisin
git clone -b raiway_network git@github.com:KyeongminNam/raisin_plugin.git
git clone -b ral_submission git@github.com:KyeongminNam/raiway_controller.git
```
- First build:
```
cd ~/raisin_network_ws
python3 raisin_workspace_setup.py
./modify_cmakelists.sh
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64
ninja -j 8
```
- Auto-start the node at boot. `/etc/systemd/system/raisin_raiway_node.service`:
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
alias build="cd ~/raisin_network_ws/build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64 && ninja -j 8 && sudo systemctl restart raisin_raiway_node.service"
alias cleanbuild="cd ~/raisin_network_ws && python3 raisin_workspace_setup.py && ./modify_cmakelists.sh && rm -rf build && mkdir build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64 && ninja -j 8 && sudo systemctl restart raisin_raiway_node.service"
alias gui="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_gui/raisin_gui/raisin_gui"
alias node="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_raiway/raisin_raiway_node"
alias realnode="cd ~/raisin_network_ws && sudo ./build/src/raisin/raisin_raiway/raisin_raiway_node real"
```

----
## Useful commands
```
sudo systemctl status raisin_raiway_node.service     # node status
journalctl -u raisin_raiway_node.service -f          # node log
sudo systemctl restart raiway_create_ap.service      # restart hotspot
```
