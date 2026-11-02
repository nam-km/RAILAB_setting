# RAILAB_setting

Setup manuals and files for RAILAB PCs (desktop, robot, operator, server).
Start with the manual for your Ubuntu version. Newer manuals replace older ones.

## Desktop PC (`linux_setting/`)
raisim2, raisin, RL training (CUDA / PyTorch), CLion.

| Manual | Ubuntu | Note |
|---|---|---|
| [Linux_setting_24.md](linux_setting/Linux_setting_24.md) | 24.04 | Driver 595, CUDA 13.2, PyTorch 2.15 |
| [Linux_setting_22.md](linux_setting/Linux_setting_22.md) | 22.04 | Driver 580, CUDA 13.0, PyTorch 2.14. Also the Jetson flashing host |
| [Linux_setting_20.md](linux_setting/Linux_setting_20.md) | 20.04 | Old notes |
| [desktop_setting.md](linux_setting/desktop_setting.md) | 20.04–24.04 | Steps common to all versions, apps, launchers, GNOME settings. Use with a version manual |

Launcher icons used by `desktop_setting.md` are in `linux_setting/files/icons/`.

## Robot PC and operator PC (`robot_setting/`)

| Manual | Device | Note |
|---|---|---|
| [Jetson_setting_2026.md](robot_setting/Jetson_setting_2026.md) | Jetson AGX Orin + CTI Rogue | Ubuntu 24.04, JetPack 7.2. Flash from a 22.04 host |
| [Onex_setting_2026.md](robot_setting/Onex_setting_2026.md) | ONEXPLAYER 2 (operator PC) | Ubuntu 24.04, dock launchers |
| [Jetson_setting_2025.md](robot_setting/Jetson_setting_2025.md) | Jetson AGX Orin | 2025 robot PC (old) |
| [Onex_setting_2025.md](robot_setting/Onex_setting_2025.md) | ONEXPLAYER 2 | 2025 operator PC (old) |

Files used by these manuals (launchers, icons, configs) are in `robot_setting/files/`.

## Lab servers (`server_setting/`)

| File | Note |
|---|---|
| [railab_server_setting.md](server_setting/railab_server_setting.md) | Server list, reservation, Docker usage |
| `Dockerfile`, `Dockerfile2` | CUDA 11.7 images on Ubuntu 20.04 / 22.04 |
| `runner.bash` | Runs a command inside the GPU Docker image with X forwarding |

## Other

| File | Note |
|---|---|
| [raisin_network.md](raisin_network.md) | raisin_network workspace setup |
| [HowtoDebug.md](HowtoDebug.md) | Debugging raisimGym envs with CLion and valgrind |
| `activation.raisim` | raisim activation key. Copy to `~/.raisim/` |
| `RAL_template.zip` | IEEE RA-L LaTeX template |
