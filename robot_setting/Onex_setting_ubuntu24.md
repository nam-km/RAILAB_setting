# OneX Setting Manual
Last Updated : 2026.11.09

Set up the OneX (operator PC) on **Ubuntu 24.04**, same as the 2025 OneX.

- Device: ONEXPLAYER 2 (AMD Ryzen 7 6800U, no NVIDIA)
- User / hostname: `raiway` / `raiway` (another username also works)
- Files: `robot_setting/files/onex/` in this repo (run the commands below from `robot_setting/`)
- raisin runs from `raisin_raion_ws`. The earlier `raisin_network_ws` sections are in [Onex_setting_ubuntu20.md](Onex_setting_ubuntu20.md) (deprecated). The ROS2 OneX is in [Onex_setting_ubuntu20_ros.md](Onex_setting_ubuntu20_ros.md).

----
## 1. Ubuntu
- Install Ubuntu 24.04.
- Settings → Displays → Orientation: the screen is a portrait panel, so pick the Portrait option that makes it landscape.
- Login screen gear icon → **Ubuntu on Xorg** (the GUI works better on Xorg).

----
## 2. Basic tools
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential ninja-build curl vim terminator \
  openssh-server python3-pip python-is-python3 htop net-tools iperf3 ffmpeg jq yq
```
- VS Code: https://code.visualstudio.com/download → `sudo apt install ./code_*_amd64.deb`
- Chrome: https://www.google.com/chrome/ → `sudo apt install ./google-chrome-stable_current_amd64.deb`
- mcfly (better Ctrl+R): https://github.com/cantino/mcfly/releases → `mcfly-*-x86_64-unknown-linux-musl.tar.gz`
```
tar -xzf mcfly-*.tar.gz && sudo mv mcfly /usr/local/bin/
```
- Terminator config:
```
mkdir -p ~/.config/terminator && cp files/onex/terminator/config ~/.config/terminator/
```
- Claude Code:
```
curl -fsSL https://claude.ai/install.sh | bash
```
- GitHub SSH key (add the `.pub` to GitHub):
```
git config --global user.name "<name>"
git config --global user.email "<email>"
ssh-keygen -t ed25519 && cat ~/.ssh/id_ed25519.pub
```

----
## 3. SSH to the robot
Connect to the robot Wi-Fi `raiway` (password `00000000`), then:
```
ssh-keygen -t rsa -f ~/.ssh/id_rsa_robot -N ""
ssh-copy-id -i ~/.ssh/id_rsa_robot.pub root@192.168.12.1
```
`~/.ssh/config` (keep the name `raiway`, the launchers use it):
```
Host raiway
    HostName 192.168.12.1
    User root
    IdentityFile ~/.ssh/id_rsa_robot
```
Check: `ssh raiway` works without a password.

If `ssh-copy-id` asks for a root password you don't have, log in as `raiway@192.168.12.1` and append `id_rsa_robot.pub` to `/root/.ssh/authorized_keys` with sudo.

----
## 4. Libraries
```
sudo apt install -y libeigen3-dev libyaml-cpp-dev libasio-dev nlohmann-json3-dev rapidjson-dev \
  libglfw3-dev libgeographiclib-dev libompl-dev libminizip-dev \
  libavdevice-dev libopus-dev libspeexdsp-dev doxygen \
  python3-numpy python3-scipy python3-pandas python3-sklearn python3-networkx \
  python3-geopandas python3-fiona python3-pyproj python3-shapely \
  python3-sphinx python3-breathe python3-sphinx-rtd-theme
```

----
## 5. raisim
raisin brings its own raisim (`install/lib/libraisim.so`). raisim2 gives the rayrai TCP viewer, which shows the robot's simulation.
```
sudo apt install -y libsdl2-dev
mkdir -p ~/.raisim && cp ../activation.raisim ~/.raisim/     # license, from the root of this repo
```
raisim2:
```
mkdir -p ~/raisim_ws && cd ~/raisim_ws
git clone git@github.com:raisimTech/raisim2Lib.git
cd raisim2Lib && source ./raisim_env.sh
cmake -S . -B build-examples -DCMAKE_BUILD_TYPE=Release -DRAISIM_EXAMPLE=ON
cmake --build build-examples --parallel $(nproc)
```
- Check: `./build-examples/examples/rayrai_tcp_viewer` (after `source ./raisim_env.sh`).

raisim (v1):
```
cd ~/raisim_ws
git clone git@github.com:raisimTech/raisimLib.git
cd raisimLib && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j8
```

----
## 6. raisin
Same workspace as the robot (`Jetson_setting_ubuntu24.md` Step 10), with the GUI and only `raisin_raiway` in `src/`. The GUI needs `raisin_raiway` for the robot model (`raiway.urdf` and the GUI world files) and for `libraiway_gui_compat.so`. The **Server On/Off** launchers use its scripts too.
Your GitHub account needs access to `raionrobotics/raisin_master` and `railabatkaist/raisin_raiway` (private).
```
git clone git@github.com:raionrobotics/raisin_master.git ~/raisin_raion_ws
cd ~/raisin_raion_ws
git submodule update --init
sudo bash install_system_deps.sh
./raisin --install && source ~/.bashrc
cp configuration_setting_example.yaml configuration_setting.yaml    # user_type: user, gh_tokens: {}
git clone git@github.com:railabatkaist/raisin_raiway.git src/raisin_raiway
raisin install raisin_gui --include-local    # the GUI and what src/raisin_raiway needs, from OTA
sudo bash install_dependencies.sh
raisin build -t release -i
```
- The OTA server must know this PC's SSH key: send `ssh-keygen -lf ~/.ssh/id_ed25519.pub` to the Raion admin. Retry tips: Troubleshooting in `raisin_manual.md` at the root of this repo.
- Run the GUI with `libraiway_gui_compat.so` preloaded (the **raisin GUI** launcher does this). Without it, the released GUI's robot window aborts on raiway's joint names.
- Don't copy the `raisin_network_ws` GUI config (`files/raisin/raisin_gui/params.yaml`, wlan0). The GUI reads `install/config/raisin_gui/config/params.yaml`, overlaid by `~/.raisin/raisin_gui/params.yaml` if that file exists.

----
## 7. ~/.bashrc
```
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
eval "$(mcfly init bash)"

alias gb="gedit ~/.bashrc"
alias sb="source ~/.bashrc"
alias unity="cd ~/raisim_ws/raisimLib/raisimUnity/linux/ && ./raisimUnity.x86_64"
alias rayrai="cd ~/raisim_ws/raisim2Lib && source ./raisim_env.sh && ./build-examples/examples/rayrai_tcp_viewer"
alias build="cd ~/raisin_raion_ws && raisin build -t release -i"
# install/ also holds the release packages, so only the build folder is removed
alias cleanbuild="cd ~/raisin_raion_ws && rm -rf cmake-build-release && raisin build -t release -i"
alias gui="~/Desktop/gui_raion.sh"
```

----
## 8. Dock launchers
| Launcher | Does |
|---|---|
| Set Time | copies the OneX clock to the robot, then deletes old `raisin_19*` logs in `/home/raiway/raisin_raion_ws/log/raisin_raiway/` |
| Server On | starts the robot node (`raisin_up.sh` on the robot, as root) |
| Server Off | stops the robot node |
| raisin GUI | opens the GUI with `libraiway_gui_compat.so` |

Run from `robot_setting/`. Only the `*_raion` launchers and Set Time: the others belong to `Onex_setting_ubuntu20.md`.
```
cp files/onex/Desktop/gui_raion.sh files/onex/Desktop/set_time.sh ~/Desktop/ && chmod +x ~/Desktop/*.sh
mkdir -p ~/.local/share/icons/raiway && cp files/onex/icons/*.png ~/.local/share/icons/raiway/
for f in settime server_on_raion server_off_raion gui_raion; do
  sed "s#^Exec=/home/raiway/#Exec=$HOME/#; s#^Icon=/home/raiway/#Icon=$HOME/#" files/onex/applications/$f.desktop > ~/.local/share/applications/$f.desktop
done
gsettings set org.gnome.shell favorite-apps "['google-chrome.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'terminator.desktop', 'code.desktop', 'settime.desktop', 'server_on_raion.desktop', 'server_off_raion.desktop', 'gui_raion.desktop']"
```
- `-f /home/raiway/raisin_raion_ws` in the Server On/Off launchers is the workspace **on the robot**, so the `sed` above leaves it alone.

Check (on `raiway` Wi-Fi): **Set Time** → **Server On** → **raisin GUI**.

----
## Useful commands
Set the robot time by hand (if **Set Time** fails). Run on the robot (`ssh raiway`):
```
sudo timedatectl set-ntp false                      # needed, or set-time is refused
sudo timedatectl set-time '2025-06-08 22:23:00'     # put the current time here
```
