# RAISIN install

For Ubuntu 22.04 / 24.04.

### Step 0. clone & system dependencies

```
git clone git@github.com:raionrobotics/raisin_master.git ~/raisin_raion_ws
cd ~/raisin_raion_ws
git submodule update --init      # vcpkg
sudo bash install_system_deps.sh
```

### Step 1. Install the raisin CLI

```
./raisin --install               # venv: ~/.venvs/raisin_master, adds a raisin function to ~/.bashrc
source ~/.bashrc
```

### Step 2. Config file

```
cp configuration_setting_example.yaml configuration_setting.yaml
```

- `user_type`: `user` (stable) / `devel` (latest)
- `gh_tokens`: only needed to clone private repos. Without one, use `gh_tokens: {}`

### Step 3. OTA authentication (SSH key)

- `~/.ssh/id_ed25519` is used automatically (for another key: `export RAISIN_SSH_KEY=~/.ssh/my_key`)
- The public key must be registered on the OTA server. Check the fingerprint:

```
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

### Step 4. Install release packages (no source)

```
raisin install --all                                # whole archive of the default tag -> release/install
raisin install --all --tag latest                   # latest development version
raisin install --all --archive-version 1.0.305      # an exact archive version (use this to match machines)
raisin install raibo2_basic_controller              # a single package
```

- Archive `raisin-robot`: 11 packages, about 2.1 GB. Takes 15 min to hours depending on the OTA server (arm64 is much slower).
- The RAILAB robot (Jetson) and OneX use **`1.0.305`** (raisin 0.4.4). See "Versions" below.
- All or nothing: if any package fails, `release/install` is not created or changed. Just run it again.
- Packages: `raisin`, `raisin_gui`, `raisin_plugin`, `raisin_raibo2`, `raibo2_basic_controller`, `raisin_robot_packages`, `raisin_robot_properties`, `raisin_ros2_messages`, `raisin_third_party_common`, `raisin_third_party_gui`, `raisin_third_party_robot`

### Step 5. Package dependencies (sudo)

```
sudo bash install_dependencies.sh
```

- Runs each package's `install_dependencies.sh` (apt packages).
- On 24.04 it skips `libgeographic-dev` and `libssh2-1`. That is fine: they are installed as `libgeographiclib-dev` and `libssh2-1t64`.

### (Optional) Develop a source package

A package cloned into `src/` takes precedence over the release package of the same name.

```
git clone git@github.com:railabatkaist/raisin_raipal.git src/raisin_raipal
raisin install                 # fetches the src package's dependencies from OTA
sudo bash install_dependencies.sh
raisin setup
raisin build -t release -i
```

### Versions

Three different numbers:

| Number | Example | What it is |
|---|---|---|
| Archive version | `1.0.305` | One OTA build: a fixed set of package versions for one platform (`ubuntu-24.04-x86_64`, `ubuntu-24.04-arm64`, ...). `N` in `1.0.N` goes up with every build. |
| Package version | `raisin 0.4.4` | The version of one package inside an archive (`release.yaml` of the package). |
| `raisin-ota-vX.Y.Z` | `raisin-ota-v0.4.0` | git tag of the installer library (`raisin_ota/` in raisin_master). Not the robot software. |

- `stable` and `latest` are OTA tags that point at an archive version, **per platform**. `user_type: user` uses `stable`, `devel` uses `latest`.
- On 2026.11.13: x86_64 24.04 `stable` = `1.0.246` (raisin 0.3.16), every platform's `latest` = `1.0.308` (raisin 0.4.4). arm64 24.04 has **no `stable`**.
- To make two machines match (robot and OneX), pin the same `--archive-version`. Since `1.0.261`, x86_64 and arm64 with the same number hold the same package versions. Before that, some numbers differ by platform (e.g. `1.0.194`–`1.0.200`).
- Every build rebuilds every package, so two archives with the same package versions still have different binaries. Pin the number, not a tag.
- raisin 0.4 starts at `1.0.285`. `1.0.305`–`1.0.308` have the same package versions.
- `release/versions/0001-1.0.305`: `0001` counts installs on this machine (used for rollback), `1.0.305` is the archive version.

### Offline install (USB)

For a machine where OTA is slow or unreachable. `robot_setting/files/raisin_release/fetch.py` downloads an archive on a PC with OTA access and packs the `release/` tree into one tarball.

```
mkdir -p ~/raisin_release && cp robot_setting/files/raisin_release/fetch.py ~/raisin_release/
cd ~/raisin_release
python3 fetch.py jetson 1.0.305        # arm64: the 7 packages the raiway src needs
python3 fetch.py controller 1.0.305    # x86_64: raisin + raisin_gui and their dependencies
```

- Needs raisin_master at `~/raisin_raion_ws` (or set `RAISIN_WS`) and OTA access (Step 3).
- Output: `~/raisin_release/<target>/<version>/raisin-<target>-<platform>-<version>.tar.gz` and `manifest.json` (package versions, sha256). Copy the version folder to a USB stick.
- `.cache/` keeps the downloaded trees, so a rerun packs again without downloading. Delete it when done.
- A tarball rather than plain files, because `release/install` is a symlink and a FAT/exFAT stick can't hold one.
- On the target, from the workspace root: `rm -rf release && tar xzf <tarball> -C ~/raisin_raion_ws`, then `sudo bash install_dependencies.sh` and `raisin build -t release -i`.

### raisin 0.3 → 0.4 (source packages)

A package in `src/` written for raisin 0.3 does not build against 0.4:

| 0.3 | 0.4 |
|---|---|
| `Robot(bool isRealRobot, ...)`, member `isRealRobot_` | `Robot(robot::RunMode runMode, ...)`, member `runMode_` (`SIM` / `REAL` / `REPLAY`, `raisin_robot/run_mode.hpp`) |
| `PluginManager(..., owner, isRealRobot)` | `PluginManager(..., owner)` |
| Plugin gets `isRealRobot` from the PluginManager | Plugin reads `runMode_` from parameter `Robot/run_mode` in its constructor |
| `real_robot: true/false` parameter | `run_mode: sim / real / replay` parameter |
| `mutable` lambda as a subscriber callback | Not allowed (called through a const copy). Keep state in a `shared_ptr` |

- A robot node that keeps its parameters under its own root (e.g. `Raiway`) must also write `Robot/run_mode` before any plugin is created, or plugins run as `sim` on the real robot.

### Locations

- Release binaries: `release/install/<package>/ubuntu/24.04/<x86_64|arm64>/release/` (`lib`, `include`, `config`, ...)
- `release/install` is a link to `release/versions/<gen>-<version>/`
- Source: `src/<package>`
- Partial downloads: `install/*.zip.part` (resumed on the next run)

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `401 Unauthorized` for every package after one slow download | OTA token lasts 15 min and the client does not renew it during one install. Run `raisin install --all` again (a fix is not in raisin_master yet). |
| `Connection broken: IncompleteRead` | OTA server dropped a slow download. Run again; the `.part` file resumes. |
| `401` right from the first package | SSH key not registered on the OTA server. Send `ssh-keygen -lf ~/.ssh/id_ed25519.pub` to the admin. |
| `raisin: command not found` | `source ~/.bashrc` |
