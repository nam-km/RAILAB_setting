# OneX Setting Manual: raisin_network_ws (deprecated)
Last Updated : 2026.11.09

**Deprecated.** These are the raisin sections from before raisin moved to `raisin_raion_ws`. They ran on the Ubuntu 24.04 OneX.
For a new OneX use [Onex_setting_ubuntu24.md](Onex_setting_ubuntu24.md). That manual also covers sections 1–5 (Ubuntu, tools, robot ssh, libraries, raisim), which these sections need.
The ROS2 (foxy) OneX is in [Onex_setting_ubuntu20_ros.md](Onex_setting_ubuntu20_ros.md).

----
## 6. raisin
Your GitHub account needs access to `railabatkaist/raisin_master` and `nam-km/raisin` (private). `install_dependencies.sh` asks y/n once.
```
mkdir ~/raisin_network_ws && cd ~/raisin_network_ws
git clone git@github.com:railabatkaist/raisin_master.git .
git clone -b raiway_network git@github.com:nam-km/raisin.git src/raisin
./src/raisin/install_dependencies.sh
echo raisin_rf > RAISIN_IGNORE
python3 raisin_workspace_setup.py
mkdir build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j 8
```

----
## 7. ~/.bashrc
```
alias build="cd ~/raisin_network_ws/build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j 8"
alias cleanbuild="cd ~/raisin_network_ws && python3 raisin_workspace_setup.py && rm -rf build && mkdir build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j 8"
alias gui="cd ~/raisin_network_ws && ./build/src/raisin/raisin_gui/raisin_gui/raisin_gui"
alias node="cd ~/raisin_network_ws && ./build/src/raisin/raisin_raiway/raisin_raiway_node"
```

----
## 8. Dock launchers
| Launcher | Does |
|---|---|
| Set Time | copies the OneX clock to the robot, then deletes old `raisin_19*` logs on the robot |
| Server On | starts the robot node |
| Server Off | stops the robot node |
| raisin network GUI | opens the GUI |

Run from `robot_setting/`. Only the network launchers: the `*_raion` ones belong to `Onex_setting_ubuntu24.md`.
```
cp files/onex/Desktop/gui_network.sh files/onex/Desktop/set_time.sh ~/Desktop/ && chmod +x ~/Desktop/*.sh
mkdir -p ~/.local/share/icons/raiway && cp files/onex/icons/*.png ~/.local/share/icons/raiway/
for f in settime server_on server_off gui_network; do
  sed "s#^Exec=/home/raiway/#Exec=$HOME/#; s#^Icon=/home/raiway/#Icon=$HOME/#" files/onex/applications/$f.desktop > ~/.local/share/applications/$f.desktop
done
gsettings set org.gnome.shell favorite-apps "['google-chrome.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'terminator.desktop', 'code.desktop', 'settime.desktop', 'server_on.desktop', 'server_off.desktop', 'gui_network.desktop']"
```
Check (on `raiway` Wi-Fi): **Set Time** → **Server On** → **raisin network GUI**.
