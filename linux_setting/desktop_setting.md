# Desktop Setting (Ubuntu 20.04 / 22.04 / 24.04)
Last Updated : 2026.11.02

Covers two things:
- Setup that is the same on Ubuntu 20.04, 22.04 and 24.04.
- The apps, launchers and GNOME settings of the lab desktop (`nkm-com`), which the version manuals don't cover.

Driver, CUDA, PyTorch, raisin, raisim, CLion and Jetson flashing steps differ by Ubuntu version and are in `Linux_setting_24.md`, `Linux_setting_22.md` and `Linux_setting_20.md`.

Order:
1. Sections 0–4 here.
2. Your version manual, steps 3–9 (driver, CUDA, conda env + PyTorch, raisin, raisim, CLion, Jetson). Skip the Miniconda install at the start of step 5, because section 4 here already did it. `Linux_setting_20.md` has no step numbers, so use its CUDA and conda notes.
3. Sections 5–9 here. The launchers in section 7 need raisim and raisin built.

The settings were read from this PC. apt package names were checked on packages.ubuntu.com for 22.04 and 24.04. Where a name differs, the note says so.

| Item | This PC (`nkm-com`) |
|---|---|
| OS | Ubuntu 20.04, GNOME 3.36, X11 session |
| CPU / RAM | Ryzen 9 5950X / 32 GB |
| GPU | RTX 3070, driver 535, CUDA 11.4 and 11.7 |
| Monitors | 2 × DELL P2722H (1920x1080), right one primary |

----
## 0. Before reinstalling
Copy these to an external disk first:
- `~/.ssh/`, `~/.bashrc`, `~/.gitconfig`, `~/.raisim/`
- `~/.config/terminator/config`, `~/.local/share/applications/`, `~/.local/share/nautilus/scripts/`
- `~/.claude/settings.json`, `~/.claude/CLAUDE.md`
- Conda envs: `conda env export -n <env> > <env>.yml` for each env in `conda env list`
- Uncommitted or unpushed work: run `git status` in each repo under `~/raisim_ws` and `~/raisin_network_ws/src`
- Training logs and data

----
## 1. Ubuntu
### Korean input
1. Settings → Region & Language → Manage Installed Languages → Install / Remove Languages → check **Korean**. On 24.04 this is under Settings → System → Region & Language.
2. `sudo apt install -y ibus-hangul`, then log out and back in.
3. Settings → Keyboard → Input Sources → **+** → Korean → **Korean (Hangul)**. On 20.04, Input Sources is under Settings → Region & Language.
4. Switch keys: this PC uses the 한/영 key (or right Alt) and Ctrl+Q instead of Shift+Space, and typing starts in English:
```
gsettings set org.freedesktop.ibus.engine.hangul switch-keys 'Hangul,Control+q,Alt_R'
gsettings set org.freedesktop.ibus.engine.hangul initial-input-mode 'latin'
```

### X11 session
```
sudo sed -i 's/^#\?WaylandEnable=.*/WaylandEnable=false/' /etc/gdm3/custom.conf
sudo reboot
```
- AnyDesk / RustDesk remote control and SimpleScreenRecorder need X11.
- Check: `echo $XDG_SESSION_TYPE` prints `x11`.

### GNOME
```
# Dock: left, always shown, small icons, no trash icon
gsettings set org.gnome.shell.extensions.dash-to-dock dock-position 'LEFT'
gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed true
gsettings set org.gnome.shell.extensions.dash-to-dock extend-height true
gsettings set org.gnome.shell.extensions.dash-to-dock dash-max-icon-size 26
gsettings set org.gnome.shell.extensions.dash-to-dock show-trash false
gsettings set org.gnome.shell.extensions.dash-to-dock show-mounts true

# Never blank or lock the screen, never suspend on AC power (training runs overnight)
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'

# No hot corner (top-left corner opening Activities)
gsettings set org.gnome.desktop.interface enable-hot-corners false
```
- Monitors: Settings → Displays. Place them side by side and set the right one as primary.

----
## 2. Basic tools
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git cmake build-essential ninja-build curl wget vim terminator tmux \
  openssh-server python3-pip python-is-python3 htop gpustat net-tools jq ffmpeg imagemagick
```
Also on this PC:
```
sudo apt install -y fzf gitk sshpass minicom rlwrap zstd speedtest-cli pandoc doxygen mesa-utils \
  fonts-nanum fonts-noto-cjk-extra ttf-mscorefonts-installer
```
- `ttf-mscorefonts-installer` shows a license screen. Press Tab to select OK, then Enter.
- On 24.04, `pip install` into the system Python is refused (`externally-managed-environment`). Use a conda env (section 4). Don't use `--break-system-packages`.

### VS Code, Chrome, mcfly
- VS Code: https://code.visualstudio.com/download → `sudo apt install ./code_*_amd64.deb`
- VS Code extensions used on this PC:
```
for e in anthropic.claude-code ms-python.python ms-toolsai.jupyter ms-vscode.cmake-tools ms-vscode.cpp-devtools \
  smilerobotics.urdf morningfrog.urdf-visualizer mtsmfm.vscode-stl-viewer \
  yzhang.markdown-all-in-one shd101wyy.markdown-preview-enhanced yzane.markdown-pdf \
  tomoki1207.pdf george-alisson.html-preview-vscode tht13.rst-vscode minim-tools.rst; do
  code --install-extension $e
done
```
- Chrome: https://www.google.com/chrome/ → `sudo apt install ./google-chrome-stable_current_amd64.deb`
- mcfly (better Ctrl+R): https://github.com/cantino/mcfly/releases → `mcfly-*-x86_64-unknown-linux-musl.tar.gz`
```
tar -xzf mcfly-*.tar.gz && sudo mv mcfly /usr/local/bin/
```

### GitHub
- SSH key (add the `.pub` to GitHub → Settings → SSH and GPG keys):
```
git config --global user.email twinhk@kaist.ac.kr
git config --global user.name KyungminNam
ssh-keygen -t ed25519 && cat ~/.ssh/id_ed25519.pub
```
- GitHub CLI (`gh`): https://github.com/cli/cli/releases → `gh_*_linux_amd64.tar.gz`
```
tar -xzf gh_*_linux_amd64.tar.gz && mkdir -p ~/.local/bin && cp gh_*_linux_amd64/bin/gh ~/.local/bin/
gh auth login        # GitHub.com → HTTPS → yes to "Authenticate Git" → log in with a web browser
```
- `gh auth login` adds `gh` as the git credential helper in `~/.gitconfig`, so HTTPS `git push` also works.

### Node.js (nvm)
Needed for the `omc` CLI and `npx`.
1. Run the `curl ... | bash` line from https://github.com/nvm-sh/nvm#install--update-script.
2. Then:
```
source ~/.bashrc
nvm install 24
```

### Claude Code
```
curl -fsSL https://claude.ai/install.sh | bash
```
oh-my-claudecode plugin (https://github.com/Yeachan-Heo/oh-my-claudecode), from a terminal:
```
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
claude plugin install oh-my-claudecode@omc
```
- Inside Claude Code, the same thing is two slash commands. Enter them one at a time: `/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode`, then `/plugin install oh-my-claudecode`.
- Then start `claude` and run `/oh-my-claudecode:omc-setup` once.
- Optional `omc` terminal command (needs Node.js): `npm i -g oh-my-claude-sisyphus`
- Check: `claude plugin list` shows `oh-my-claudecode@omc`.

### Codex
```
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

----
## 3. Terminal (Terminator)
Make Terminator the default terminal:
```
gsettings set org.gnome.desktop.default-applications.terminal exec terminator
sudo update-alternatives --set x-terminal-emulator /usr/bin/terminator
```
- If Ctrl+Alt+T still opens GNOME Terminal, add a shortcut in Settings → Keyboard → Custom Shortcuts with command `terminator` and key Ctrl+Alt+T.

`~/.config/terminator/config`:
```
mkdir -p ~/.config/terminator && cat > ~/.config/terminator/config <<'EOF'
[global_config]
  title_transmit_fg_color = "#000000"
  title_transmit_bg_color = "#eeeeec"
  suppress_multiple_term_dialog = True
[keybindings]
  broadcast_off = <Super>o
  broadcast_group = <Super>g
  broadcast_all = <Super>a
  layout_launcher = F3
[profiles]
  [[default]]
    cursor_color = "#aaaaaa"
    foreground_color = "#ffffff"
    scrollback_infinite = True
[layouts]
  [[default]]
    [[[window0]]]
      type = Window
      parent = ""
    [[[child1]]]
      type = Terminal
      parent = window0
[plugins]
EOF
```
- Super+A types into all panes at once, Super+G into the group, Super+O turns this off. Scrollback is unlimited.

Programs that use `x-terminal-emulator`, such as VS Code's "Open in External Terminal" on Ubuntu, already get Terminator from the `update-alternatives` line above. Programs that start `gnome-terminal` by name get Terminator through this wrapper, because `/usr/local/bin` comes before `/usr/bin` in PATH:
```
sudo tee /usr/local/bin/gnome-terminal > /dev/null <<'EOF'
#!/bin/bash
# Redirect gnome-terminal to Terminator. Keeps only --working-directory.
WD=""
while [ $# -gt 0 ]; do
  case "$1" in
    --working-directory=*) WD="${1#*=}"; shift ;;
    --working-directory)   shift; WD="$1"; shift ;;
    *) shift ;;
  esac
done
if [ -n "$WD" ]; then exec terminator --working-directory="$WD"; else exec terminator; fi
EOF
sudo chmod +x /usr/local/bin/gnome-terminal
```

Nautilus right-click → Scripts → **Open in Terminator**:
```
mkdir -p ~/.local/share/nautilus/scripts
cat > ~/.local/share/nautilus/scripts/"Open in Terminator" <<'EOF'
#!/bin/bash
# Opens the selected folder, or the folder you are in.
SEL=$(printf '%s\n' "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" | head -n1)
if [ -d "$SEL" ]; then
  DIR=$SEL
else
  DIR=$(python3 -c 'import sys, urllib.parse as u; print(u.unquote(u.urlparse(sys.argv[1]).path))' "$NAUTILUS_SCRIPT_CURRENT_URI")
fi
exec terminator --working-directory="$DIR"
EOF
chmod +x ~/.local/share/nautilus/scripts/"Open in Terminator"
```
- The `python3` line decodes the folder URI, so paths with spaces or Korean names work.

----
## 4. Miniconda
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh        # answer yes to conda init
source ~/.bashrc
conda config --set auto_activate_base false
```
- Create the `raisim` env and install PyTorch and the training packages with your version manual (step 5). The Python version, CUDA wheel and package pins differ per Ubuntu version.
- Every raisimGym env needs `ruamel.yaml<0.18`: raisimGym imports `ruamel.yaml.dump`, which 0.18 removed.
- wandb: make an account at https://wandb.ai/site, then `wandb login` and paste the key from https://wandb.ai/authorize.

----
## 5. Applications
apt:
```
sudo apt install -y inkscape vlc pdfarranger peek simplescreenrecorder blender meshlab \
  libreoffice libreoffice-l10n-ko libreoffice-help-ko
```
- Ubuntu's Inkscape on 20.04 is old (0.92). This PC uses Inkscape 1.3 from the PPA: `sudo add-apt-repository ppa:inkscape.dev/stable`, then install.

LaTeX (for `RAL_template.zip` in this repo, which ships its own `IEEEtran.cls`):
```
sudo apt install -y texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
  texlive-pictures texlive-extra-utils
```

Others:

| App | Install | Note |
|---|---|---|
| Teams | `sudo snap install teams-for-linux` | Unofficial client |
| Notion | `sudo snap install notion-desktop` | Unofficial client |
| MD Viewer | `sudo snap install md-viewer` | Default app for `.md` (see below) |
| Zoom | https://zoom.us/download?os=linux → `sudo apt install ./zoom_amd64.deb` | |
| Synology Chat | Synology Download Center → Synology Chat Client (`.deb`) → `sudo apt install ./*.deb` | |
| AnyDesk | https://anydesk.com/en/downloads/linux → `.deb` | Runs as a service, starts at boot |
| RustDesk | https://github.com/rustdesk/rustdesk/releases → `rustdesk-*-x86_64.deb` | Runs as a service, starts at boot |
| Bambu Studio | https://github.com/bambulab/BambuStudio/releases → AppImage for your Ubuntu version | 3D printer slicer. Commands below |
| MATLAB R2020a | MathWorks installer → `/usr/local/MATLAB/R2020a` | |
| CARLA 0.9.16 | https://github.com/carla-simulator/carla/releases → `CARLA_0.9.16.tar.gz` | Commands below |

Bambu Studio (AppImages need FUSE 2):
```
sudo apt install -y libfuse2          # 24.04: libfuse2t64
sudo install -m 755 Bambu_Studio_*.AppImage /opt/Bambu_Studio.AppImage
```
CARLA:
```
mkdir ~/CARLA_0.9.16 && tar -xzf CARLA_0.9.16.tar.gz -C ~/CARLA_0.9.16
cd ~/CARLA_0.9.16 && ./CarlaUE4.sh
```
Open `.md` files with MD Viewer:
```
xdg-mime default md-viewer_md-viewer.desktop text/markdown
```

----
## 6. ROS 2 and RealSense
ROS 2: the version manuals' `cwbs` / `cws` aliases (`~/raisin_ws`) need it.

| Ubuntu | ROS 2 |
|---|---|
| 20.04 | Foxy (end of life since 2023; on this PC) |
| 22.04 | Humble |
| 24.04 | Jazzy |

1. Add the ROS 2 apt repo with https://docs.ros.org/en/<distro>/Installation.html → Ubuntu (deb packages).
2. Then:
```
sudo apt install -y ros-<distro>-desktop python3-colcon-common-extensions
echo "source /opt/ros/<distro>/setup.bash" >> ~/.bashrc
```
- Extra packages on this PC: `ros-foxy-pcl-ros ros-foxy-camera-info-manager ros-foxy-compressed-image-transport ros-foxy-ublox-msgs`.

RealSense (librealsense 2.56 on this PC):
1. Add Intel's apt repo with https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md.
2. Then:
```
sudo apt install -y librealsense2-dkms librealsense2-utils librealsense2-dev
```
- Check: plug in the camera and run `realsense-viewer`.

----
## 7. Desktop launchers and dock
| Launcher | Runs |
|---|---|
| raisimUnity | `~/raisim_ws/raisimLib/raisimUnity/linux/raisimUnity.x86_64` |
| raisimUnreal | `~/Downloads/Linux/raisimUnreal2.sh` |
| raisin gui | raisin GUI in `~/raisin_network_ws/build` |
| RaiSim2 TCP Viewer | `rayrai_tcp_viewer` after `source raisim_env.sh` (same as the `ru2` alias) |
| Bambu Studio | `/opt/Bambu_Studio.AppImage` |
| MATLAB | `/usr/local/MATLAB/R2020a/bin/matlab -desktop` |

Run from `linux_setting/` in this repo (the icons are in `files/icons/`):
```
mkdir -p ~/.local/share/icons/railab ~/.local/share/applications ~/.local/bin
cp files/icons/*.png ~/.local/share/icons/railab/
A=$HOME/.local/share/applications
I=$HOME/.local/share/icons/railab

# rayrai_tcp_viewer needs raisim_env.sh (library paths), so its launcher runs this script
cat > ~/.local/bin/rayrai-tcp-viewer <<'EOF'
#!/usr/bin/env bash
cd "$HOME/raisim_ws/raisim2Lib"
source ./raisim_env.sh
exec ./build-examples/examples/rayrai_tcp_viewer "$@"
EOF
chmod +x ~/.local/bin/rayrai-tcp-viewer

cat > $A/raisimUnity.desktop <<EOF
[Desktop Entry]
Type=Application
Name=raisimUnity
Exec=$HOME/raisim_ws/raisimLib/raisimUnity/linux/raisimUnity.x86_64
Icon=$I/raisimUnity.png
Categories=Development;
EOF

cat > $A/raisimUnreal.desktop <<EOF
[Desktop Entry]
Type=Application
Name=raisimUnreal
Exec=$HOME/Downloads/Linux/raisimUnreal2.sh
Icon=$I/raisimUnreal.png
Categories=Development;
StartupWMClass=raisimUnreal2-Linux-Shipping
EOF

cat > $A/raisin-gui.desktop <<EOF
[Desktop Entry]
Type=Application
Name=raisin gui
Exec=$HOME/raisin_network_ws/build/src/raisin/raisin_gui/raisin_gui/raisin_gui
Path=$HOME/raisin_network_ws
Icon=$I/raisin-gui.png
Categories=Development;
StartupWMClass=raisin gui
EOF

cat > $A/rayrai-tcp-viewer.desktop <<EOF
[Desktop Entry]
Type=Application
Name=RaiSim2 TCP Viewer
Exec=$HOME/.local/bin/rayrai-tcp-viewer
Icon=$I/rayrai-tcp-viewer.png
Categories=Science;Engineering;
EOF

cat > $A/bambu_studio.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Bambu Studio
Exec=/opt/Bambu_Studio.AppImage
Icon=$I/bambu-studio.png
Categories=Graphics;
StartupWMClass=BambuStudio
EOF

cat > $A/matlab.desktop <<EOF
[Desktop Entry]
Type=Application
Name=MATLAB
Exec=/usr/local/MATLAB/R2020a/bin/matlab -desktop
Icon=/usr/local/MATLAB/R2020a/toolbox/shared/Matlab_Logo.png
Categories=Development;
EOF
```
- `.desktop` files don't expand `~` or `$HOME`. The heredocs write your real home path into them, so run the block as your own user.
- `StartupWMClass` makes the running window group under the launcher's dock icon.

Dock, in this PC's order:
```
gsettings set org.gnome.shell favorite-apps "['google-chrome.desktop', 'gnome-control-center.desktop', 'org.gnome.Nautilus.desktop', 'terminator.desktop', 'code.desktop', 'jetbrains-clion.desktop', 'teams-for-linux_teams-for-linux.desktop', 'bambu_studio.desktop', 'notion-desktop_notion-desktop.desktop', 'rayrai-tcp-viewer.desktop', 'raisimUnity.desktop', 'raisimUnreal.desktop']"
```
- On 24.04, Settings is `org.gnome.Settings.desktop`. CLion from snap is `clion_clion.desktop`. `jetbrains-clion.desktop` comes from a tar.gz CLion (CLion → Tools → Create Desktop Entry), as on this PC.
- Check: press Super, type `raisim`, and the launchers show with their icons.

----
## 8. Remote access
- SSH server: `openssh-server` (section 2).
- AnyDesk and RustDesk (section 5) run as services and start at boot. They need the X11 session (section 1). Check: `systemctl is-enabled anydesk rustdesk`.
- `~/.ssh/config` entries for the robot (connect to the robot's Wi-Fi first):
```
Host robot2
    HostName 192.168.12.1
    User root
Host raibo2
    HostName 192.168.12.1
    User raibo2
```

----
## 9. ~/.bashrc
conda, nvm and ROS 2 add their own lines. Keep those, then add the block below. Its first two lines are the CUDA lines from the version manual's step 4, so don't add them twice.
```
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
export PATH=$HOME/.local/bin:$PATH
export LANG=en_US.UTF-8
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

# raisin_ws (ROS 2, section 6)
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
- Keep API keys out of this block: it gets copied between PCs and into this repo.

----
## Useful commands
```
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches     # free the page cache (memory check)
gpustat -i 1                                          # GPU usage, refreshed every second
```

----
## Appendix: Ubuntu 20.04 (this PC)
- CUDA: `/usr/local/cuda` points to 11.4, which SDK Manager installed with the JetPack 5.1.3 host components (aarch64 cross toolkit, Nsight, VPI 2). CUDA 11.7 is also installed (`Linux_setting_20.md`).
- raisim2 doesn't build with Ubuntu 20.04's defaults:
  - cmake 3.16 is older than the 3.18 raisim2Lib needs.
  - g++ 9 has no `<span>`, which rayrai uses.
  - libsdl2-dev 2.0.10 doesn't define the `SDL2::SDL2` target.
- Build it like this:
```
sudo apt install -y g++-10 libsdl2-dev
conda create -n raisim2 python=3.9 && conda activate raisim2 && pip install cmake

cd ~/raisim_ws/raisim2Lib
mkdir -p sdl2_cmake_fix && cat > sdl2_cmake_fix/SDL2Config.cmake <<'EOF'
# Ubuntu 20.04's libsdl2-dev (2.0.10) ships only variables, but rayraiTargets.cmake links SDL2::SDL2.
find_path(SDL2_INCLUDE_DIR SDL.h PATH_SUFFIXES SDL2)
find_library(SDL2_LIBRARY NAMES SDL2-2.0 SDL2)
find_library(SDL2_MAIN_LIBRARY NAMES SDL2main)
if(NOT SDL2_INCLUDE_DIR OR NOT SDL2_LIBRARY)
  message(FATAL_ERROR "SDL2 headers or library not found; install libsdl2-dev")
endif()
if(NOT TARGET SDL2::SDL2)
  add_library(SDL2::SDL2 SHARED IMPORTED)
  set_target_properties(SDL2::SDL2 PROPERTIES
    IMPORTED_LOCATION "${SDL2_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${SDL2_INCLUDE_DIR}")
endif()
if(SDL2_MAIN_LIBRARY AND NOT TARGET SDL2::SDL2main)
  add_library(SDL2::SDL2main STATIC IMPORTED)
  set_target_properties(SDL2::SDL2main PROPERTIES IMPORTED_LOCATION "${SDL2_MAIN_LIBRARY}")
endif()
set(SDL2_INCLUDE_DIRS "${SDL2_INCLUDE_DIR}")
set(SDL2_LIBRARIES SDL2::SDL2)
set(SDL2_FOUND TRUE)
EOF

source ./raisim_env.sh && export RAISIM_LOCAL_INSTALL_ROOT=$PWD
cmake -S . -B build-examples -DCMAKE_BUILD_TYPE=Release -DRAISIM_EXAMPLE=ON \
  -DSDL2_DIR=$PWD/sdl2_cmake_fix -DCMAKE_CXX_COMPILER=g++-10
cmake --build build-examples --parallel $(nproc)
```
- `sdl2_cmake_fix/` isn't part of the raisim2Lib git repo. After a fresh clone, create it again.
