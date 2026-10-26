# Jetson Setting Manual
Last Updated : 2025.02.24

----
## step 0: Install sdkmanager to desktop
- download sdkmanager: https://developer.nvidia.com/sdk-manager
```
sudo apt update
sudo apt install libnss3-tools libcanberra-gtk-module
sudo apt install ./sdkmanager_2.1.0-11698_amd64.deb
sudo apt --fix-broken install # if error occured
```
- run `sdkmanager`


- enable ssh of desktop
```
sudo apt-get update
sudo apt-get install openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
```

----
## Step 1: Install CTI-L4T & BSP
Follow: https://connecttech.com/resource-center/kdb373/
- desktop 20.04, jetpack 5.1.3
- Target Components -> uncheck "Jetson SDK components".
- 2 Pop ups (SDK Manager is about to flash..., sdk manager is about to install sdk components... ) -> skip
- Install finish

#### BSP (Board Support Package)
- download link: https://connecttech.com/resource-center/l4t-board-support-packages/
- select right version and download .tgz 
- move .tgz to folder `~/nvidia/nvidia_sdk/JetPack_5.1.3_Linux_JETSON_AGX_ORIN_TARGETS/Linux_for_Tegra`

```
# Linux_for_Tegra directory
tar -xzvf CTI-L4T-ORIN-AGX-35.5.0-V002.tgz
cd CTI-L4T
sudo ./install.sh
cd .. # return to the Linux_for_Tegra directory
```

- After `sudo ./install.sh`, you can see
```
Success!
/home/nkm/nvidia/nvidia_sdk/JetPack_5.1.3_Linux_JETSON_AGX_ORIN_TARGETS/Linux_for_Tegra/CTI-L4T
CTI-L4T-ORIN-AGX-35.5.0-V002 Installed!
```
- and if you run `lsusb` in folder `Linux_for_Tegra`, you can see  
```
...
Bus 001 Device 016: ID 0955:7223 NVIDIA Corp.
...

```
- run `sudo ./cti-flash.sh` select `rogue-orin` - `base` - `orin-agx`
- takes very long time. If done, you can see
```
*** The target t186ref has been flashed successfully. ***
Reset the board to boot from internal eMMC.
```


Next, see the jetson screen. Install the SW (Similar to Ubuntu install)
- install chromium browser
- install, reset, and connect internet
- remember username and password!

----
## Step 2: Jetpack SDK Components
Follow : https://connecttech.com/resource-center/kdb374/
- `sdkmanager` -> Target Components: except Jetson Linux
- Pop-up -> enter the username/password created in jetson
- It takes very long time to install
- 
You must see INSTALLATION COMPLETED SUCCESSFULLY

----

## Step 3: Mount SSD

Follow: https://semotube.tistory.com/m/98  

- format ssd, make partition to ext4  
```
git clone https://github.com/jetsonhacks/rootOnNVMe.git 
cd rootOnNVMe
./copy-rootfs-ssd.sh
./setup-service.sh
sudo reboot
```

----

## Step 4: Linux setting

```
sudo apt -y update
sudo apt -y upgrade
sudo apt -y autoremove
sudo apt -y autoclean
sudo apt -y --fix-broken install
sudo apt-get remove --purge XXX
```

### install ros2 foxy  
https://docs.ros.org/en/foxy/Installation.html

### install vscode for arm64

### git ssh setting  
```
ssh-keygen
gedit ~/.ssh/id_rsa.pub
```

### install raisim & raisin
- raisim
```
#mkdir ~/raisim_ws && cd ~/raisim_ws/
git clone git@github.com:raisimTech/raisimLib.git
cd ~/raisim_ws/raisimLib && mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
#cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_PROCESSOR=aarch64
make -j16
```

- raisin (ros)
```
# mkdir -p ~/raisin_ws/src && cd ~/raisin_ws/src
# clone raisin / raisin_plugin / raiway_controller
# set proper branch
# change CMakelists.txt of raisin_raisimlib
```

- raisin (network)
```
Sphinx                               4.5.0
sphinx-panels                        0.6.0
sphinx-rtd-theme                     1.0.0
sphinx-tabs                          3.4.7
sphinxcontrib-applehelp              1.0.4
sphinxcontrib-devhelp                1.0.2
sphinxcontrib-htmlhelp               2.0.1
sphinxcontrib-jquery                 4.1
sphinxcontrib-jsmath                 1.0.1
sphinxcontrib-qthelp                 1.0.3
sphinxcontrib-serializinghtml        1.1.5
sphinxcontrib-youtube                1.3.0
```


### install dependencies

- realsense SDK
```
## Step1
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null

## Step2
echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo `lsb_release -cs` main" | \
sudo tee /etc/apt/sources.list.d/librealsense.list
sudo apt-get update

## Step3
sudo apt-get install -y librealsense2-dkms librealsense2-utils 
sudo apt-get install -y librealsense2-dev librealsense2-dbg
```

- PCL-ROS
```
sudo apt install ros-foxy-pcl-ros
```

- yq
```
sudo add-apt-repository ppa:rmescandon/yq
sudo apt update
sudo apt install yq -y
```

- ssh
```
sudo apt install openssh-server 
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod og-wx ~/.ssh/authorized_keys 
```

- gui
```
sudo apt install python3-pip
pip install osmnx
pip install scikit-learn

sudo apt-get install ros-foxy-compressed-image-transport
sudo apt install ros-foxy-camera-info-manager*
sudo apt-get install libglfw3 libglfw3-dev
sudo apt install libompl-dev
sudo apt install libgeographic-dev
```

- etc
```
sudo apt install python3-colcon-common-extensions -y
sudo apt install git cmake minizip libeigen3-dev

sudo apt install python3-rosdep -y
sudo rosdep init
rosdep update
```
```
sudo apt install libyaml-cpp-dev -y
sudo apt install -y libpostproc-dev libavdevice-dev libavfilter-dev
sudo apt install g++-aarch64-linux-gnu libc6-dev -y
sudo apt install pkg-config -y

sudo apt install libopencv-dev python3-opencv -y
sudo apt install ros-foxy-vision-opencv ros-foxy-cv-bridge -y
sudo apt install ros-foxy-image-transport -y
sudo apt install ros-foxy-eigen3-cmake-module -y
sudo apt install ros-foxy-rosidl-default-generators -y
sudo apt install ros-foxy-ament-cmake ros-foxy-ament-lint-auto 
sudo apt install ros-foxy-ament-cmake-auto -y
sudo apt install ros-foxy-rclcpp-components -y
sudo apt install ros-foxy-std-srvs -y
sudo apt install ros-foxy-sdl2-vendor libsdl2-dev -y
sudo apt install ros-foxy-ublox-msgs -y
sudo apt install ros-foxy-compressed-image-transport -y

sudo apt install ffmpeg
```

### create_ap
- clone
```
cd ~ && git clone git@github.com:oblique/create_ap.git
cd ~/create_ap
make install
```

- write to ~/create_ap/make_ap.py
```
import os
os.system("chmod 666 /dev/ttyACM0")
os.system("sudo create_ap -n wlan0 'raiway' '00000000' --freq-band 2.4 --no-virt -w 2 -c 6 --ieee80211n")
```

- write to /etc/systemd/system/raiway_create_ap.service
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

- how to use
```
sudo systemctl enable raiway_create_ap.service
sudo systemctl start raiway_create_ap.service
sudo systemctl status raiway_create_ap.service
sudo systemctl stop raiway_create_ap.service
```
### lancard setup
1) check lancard version with `lspci` or `sudo lshw -C network`
- For example, `0005:03:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL8125 2.5GbE Controller (rev 05)`, then RTL8125 is my lancard  
2) download driver in : https://www.realtek.com/Download/List?cate_id=584
3) 
```
tar -xvf r8125-9.005.06.tar.bz2
cd r8125-9.005.06
sudo ./autorun.sh
# You must see "complete"

sudo reboot
```

4) check slaveinfo with SOEM
`sudo ./slaveinfo eth0`

5) change name `ethX` to `ethercat`


### SOEM
- clone & build
```
cd ~ && git clone git@github.com:OpenEtherCATsociety/SOEM.git
cd ~/SOEM
mkdir build
cd build 
cmake ..
make
```

- how to use
```
cd ~/SOEM/build/test/linux/simple_test/
sudo ./simple_test XXX

cd ~/SOEM/build/test/linux/slaveinfo/
sudo ./slaveinfo XXX
```

### auto-start the raisin(network) raiway node
In robot PC,
`vi /etc/systemd/system/raisin_raiway_node.service`

```
[Unit]
Description=raisin raiway node
After=network.target

[Service]
Type=simple
# Path to your executable or script
ExecStart=/home/raiway/raisin_ws/install/scripts/raisin_raiway/scripts/raisin_service.sh
# Ensure the service will be automatically restarted if it crashes
Restart=always
RestartSec=2
# Run as root (You can specify a different user if necessary)
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

```
systemctl daemon-reload
systemctl enable raisin_raibo2_node.service
systemctl start raisin_raibo2_node.service
```