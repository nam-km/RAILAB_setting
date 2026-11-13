#!/usr/bin/env python3
"""Fetch a raisin OTA archive for an offline machine and pack it for USB.

    python3 fetch.py jetson     1.0.305
    python3 fetch.py controller 1.0.305

Writes <target>/<version>/ next to this file:
    raisin-<target>-<platform>-<version>.tar.gz   the release/ tree
    manifest.json                                 archive, packages, sha256

On the target machine, extract the tarball at the raisin workspace root so that
`release/` lands next to raisin.py (an existing release/ is replaced):
    tar xzf raisin-<...>.tar.gz -C ~/raisin_ws

A tarball rather than a plain copy: `release/install` is a symlink, which a
FAT/exFAT USB stick cannot hold.

The unpacked tree is kept under .cache/<target>/<version>/ and reused, so a
rerun (to repack, or after an interrupted pack) does not download again.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get("RAISIN_WS", Path.home() / "raisin_raion_ws"))
sys.path.insert(0, str(WORKSPACE))

from raisin_ota import client as ota  # noqa: E402

ARCHIVE = "raisin-robot"
TARGETS = {
    # target: (os_version, architecture, root packages; their dependencies come along)
    # jetson: what the raiway src packages build against.
    "jetson": ("24.04", "arm64",
               ["raisin", "raisin_plugin", "raisin_robot_packages",
                "raisin_third_party_common", "raisin_third_party_robot"]),
    "controller": ("24.04", "x86_64", ["raisin", "raisin_gui"]),
}


def _name(dep):
    for sep in "<>=!":
        dep = dep.split(sep)[0]
    return dep.strip()


def _deps(install, name, os_version, arch):
    f = install / name / "ubuntu" / os_version / arch / "release" / "release.yaml"
    if not f.exists():
        return None  # not downloaded yet
    return [_name(d) for d in (yaml.safe_load(f.read_text()) or {}).get("dependencies") or []]


def _closure(install, roots, os_version, arch):
    """(closure, missing): the packages roots need, and those not downloaded yet."""
    seen, missing, todo = set(), set(), list(roots)
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        deps = _deps(install, name, os_version, arch)
        if deps is None:
            missing.add(name)
        else:
            todo.extend(deps)
    return sorted(seen), missing


def _live_version(release):
    link = release / "install"
    return os.readlink(link).split("-", 1)[1] if link.is_symlink() else None


def stage(target, version):
    os_version, arch, roots = TARGETS[target]
    cache = HERE / ".cache" / target / version
    release = cache / "release"
    install = release / "install"
    cache.mkdir(parents=True, exist_ok=True)
    # OTA token, state and zip cache stay in .cache, out of what goes on the stick.
    ota.configure(ota.OtaContext(
        workspace=cache, os_type="ubuntu", os_version=os_version, architecture=arch,
    ))
    if install.exists() and _live_version(release) != version:
        sys.exit(f"{release} holds {_live_version(release)}, not {version}; remove it first")

    # Dependencies are declared inside each package: fetch what is missing, read
    # what landed, repeat until the closure is complete.
    while True:
        closure, missing = _closure(install, roots, os_version, arch)
        if not missing:
            break
        print(f"⬇️  {target}: fetching {', '.join(sorted(missing))}")
        if not ota.download_all_from_archive(
            "release", install, archive_version=version, archive_name=ARCHIVE,
            package_filter=sorted(missing), report_snapshot=False,
        ):
            sys.exit("download failed")

    for pkg in install.iterdir():
        if pkg.is_dir() and pkg.name not in closure:
            shutil.rmtree(pkg)
    live = install.resolve()
    for gen in (release / "versions").iterdir():
        if gen.resolve() != live:
            shutil.rmtree(gen)
    (release / ".rollback").unlink(missing_ok=True)
    return release, closure


def pack(target, version, release, closure):
    os_version, arch, _ = TARGETS[target]
    platform = f"ubuntu-{os_version}-{arch}"
    out = HERE / target / version
    out.mkdir(parents=True, exist_ok=True)
    tarball = out / f"raisin-{target}-{platform}-{version}.tar.gz"
    tmp = tarball.with_suffix(".part")
    with tarfile.open(tmp, "w:gz") as tar:
        tar.add(release, arcname="release")
    tmp.rename(tarball)

    sha = hashlib.sha256()
    with open(tarball, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha.update(chunk)
    packages = {}
    for name in closure:
        meta = release / "install" / name / "ubuntu" / os_version / arch / "release" / "release.yaml"
        packages[name] = (yaml.safe_load(meta.read_text()) or {}).get("version")
    manifest = {
        "archive": ARCHIVE, "archive_version": version, "platform": platform,
        "file": tarball.name, "sha256": sha.hexdigest(), "bytes": tarball.stat().st_size,
        "packages": packages,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"📦 {tarball} ({tarball.stat().st_size / 2**20:.0f} MiB)")
    for name, ver in packages.items():
        print(f"   {name} {ver}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=sorted(TARGETS))
    ap.add_argument("archive_version")
    args = ap.parse_args()
    release, closure = stage(args.target, args.archive_version)
    pack(args.target, args.archive_version, release, closure)


if __name__ == "__main__":
    main()
