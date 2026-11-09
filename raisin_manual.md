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
raisin install --all                     # whole archive -> release/install
raisin install --all --tag latest        # latest development version
raisin install raibo2_basic_controller   # a single package
```

- `stable` archive (`raisin-robot v1.0.246`): 11 packages, about 2.1 GB. Takes 15 min to hours depending on the OTA server.
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

### Locations

- Release binaries: `release/install/<package>/ubuntu/24.04/x86_64/release/` (`lib`, `include`, `config`, ...)
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
