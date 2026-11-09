# Jetson Setting Manual: raisin_network_ws (deprecated)
Last Updated : 2026.11.09

**Deprecated.** This is the raisin step from before raisin moved to `raisin_raion_ws`. It ran on the Ubuntu 24.04 Jetson.
For a new robot PC use [Jetson_setting_ubuntu24.md](Jetson_setting_ubuntu24.md). That manual also covers Steps 0–9 (flashing, tools, raisim, EtherCAT, hotspot), which this step needs.
The ROS2 (foxy) robot PC is in [Jetson_setting_ubuntu20_ros.md](Jetson_setting_ubuntu20_ros.md).

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
- `nam-km/raiway_controller` is archived. The same history, branches included, is in `railabatkaist/raiway_controller`.
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
