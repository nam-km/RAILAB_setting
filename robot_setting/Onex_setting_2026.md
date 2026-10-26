# OneX Setting Manual
Last Updated : 2026.10.26

Set up the OneX (operator PC) on **Ubuntu 24.04**, same as the 2025 OneX.

- Device: ONEXPLAYER 2 (AMD Ryzen 7 6800U, no NVIDIA)
- User / hostname: `raiway` / `raiway` (another username also works)
- Files: `robot_setting/files/onex/` in this repo (run the commands below from `robot_setting/`)

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
```
mkdir ~/raisim_ws && cd ~/raisim_ws
git clone git@github.com:raisimTech/raisimLib.git
cd raisimLib && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j8
```

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
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
eval "$(mcfly init bash)"

alias gb="gedit ~/.bashrc"
alias sb="source ~/.bashrc"
alias unity="cd ~/raisim_ws/raisimLib/raisimUnity/linux/ && ./raisimUnity.x86_64"
alias build="cd ~/raisin_network_ws/build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j 8"
alias cleanbuild="cd ~/raisin_network_ws && python3 raisin_workspace_setup.py && rm -rf build && mkdir build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release && ninja -j 8"
alias gui="cd ~/raisin_network_ws && ./build/src/raisin/raisin_gui/raisin_gui/raisin_gui"
alias node="cd ~/raisin_network_ws && ./build/src/raisin/raisin_raiway/raisin_raiway_node"
```

----
## 8. Dock launchers
| Launcher | Does |
|---|---|
| Set Time | copies the OneX clock to the robot, then deletes old `raisin_19*` logs in `/home/raiway/raisin_network_ws/log/raisin_raiway/` |
| Server On | starts the robot node |
| Server Off | stops the robot node |
| raisin network GUI | opens the GUI |

```
cp files/onex/Desktop/*.sh ~/Desktop/ && chmod +x ~/Desktop/*.sh
mkdir -p ~/.local/share/icons/raiway && cp files/onex/icons/*.png ~/.local/share/icons/raiway/
for f in files/onex/applications/*.desktop; do
  sed "s#^Exec=/home/raiway/#Exec=$HOME/#; s#^Icon=/home/raiway/#Icon=$HOME/#" "$f" > ~/.local/share/applications/$(basename "$f")
done
gsettings set org.gnome.shell favorite-apps "['google-chrome.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'terminator.desktop', 'code.desktop', 'settime.desktop', 'server_on.desktop', 'server_off.desktop', 'gui_network.desktop']"
```
Check (on `raiway` Wi-Fi): **Set Time** → **Server On** → **raisin network GUI**.

----
## Useful commands
Set the robot time by hand (if **Set Time** fails). Run on the robot (`ssh raiway`):
```
sudo timedatectl set-ntp false                      # needed, or set-time is refused
sudo timedatectl set-time '2025-06-08 22:23:00'     # put the current time here
```
