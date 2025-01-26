from typing import Final
import urllib.request
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    name: str
    browser_download_url: str
    state: str
    size: int


@dataclass(frozen=True)
class Release:
    name: str
    tag_name: str
    draft: bool
    prerelease: bool
    assets: list[Asset]


@dataclass(frozen=True)
class PlatformConfig:
    marker: str
    path: str


PLATFORMS: Final[dict[str, PlatformConfig]] = {
    "linux-aarch64": PlatformConfig(
        marker="aarch64-unknown-linux-gnu-lto-full",
        path="python/install/bin/python",
    ),
    "linux-x86_64": PlatformConfig(
        marker="x86_64_v3-unknown-linux-gnu-pgo+lto-full",
        path="python/install/bin/python",
    ),
    "macos-aarch64": PlatformConfig(
        marker="aarch64-apple-darwin-pgo+lto-full",
        path="python/install/bin/python",
    ),
    "macos-x86_64": PlatformConfig(
        marker="x86_64-apple-darwin-pgo+lto-full",
        path="python/install/bin/python",
    ),
    # "windows-aarch64": PlatformConfig(...),
    "windows-x86_64": PlatformConfig(
        marker="x86_64-pc-windows-msvc-shared-pgo-full",
        path="python/install/python.exe",
    ),
}

PYTHON_VERSION = "3.13"


def fetch_latest_release() -> Release:
    with urllib.request.urlopen(
        "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
    ) as response:
        if response.status != 200:
            raise RuntimeError(f"Failed to fetch release info: {response.status}")
        release_data = json.loads(response.read())
        return Release(
            name=release_data["name"],
            tag_name=release_data["tag_name"],
            draft=release_data["draft"],
            prerelease=release_data["prerelease"],
            assets=[
                Asset(
                    name=asset["name"],
                    browser_download_url=asset["browser_download_url"],
                    state=asset["state"],
                    size=asset["size"],
                )
                for asset in release_data["assets"]
            ],
        )


def find_asset_for_platform(release: Release, platform: str) -> Asset:
    ret: list[Asset] = []
    marker = PLATFORMS[platform].marker
    for asset in release.assets:
        if not asset.name.startswith(f"cpython-{PYTHON_VERSION}"):
            continue
        if asset.name.endswith(".sha256"):
            continue
        if marker in asset.name:
            ret.append(asset)
    if len(ret) > 1:
        raise ValueError(
            f"More than one asset matches {marker!r} for {platform=}. Candidates: {[a.name for a in ret]}"
        )
    if len(ret) == 0:
        raise ValueError(f"No assets found for {platform=} in {release.name=}")
    return ret[0]


def platform_descriptor(platform: str, asset: Asset) -> object:
    extension = "tar.zst"
    if not asset.browser_download_url.endswith(extension):
        raise ValueError(
            f"Asset for {platform=} isn't supported by dotslash: {asset.browser_download_url}"
        )
    with urllib.request.urlopen(f"{asset.browser_download_url}.sha256") as response:
        if response.status != 200:
            raise RuntimeError(
                f"Failed to fetch digest for {asset.browser_download_url}: {response=}"
            )
        digest = bytes(response.read().strip()).decode()
    return {
        "size": asset.size,
        "hash": "sha256",
        "digest": digest,
        "format": extension,
        "path": PLATFORMS[platform].path,
        "providers": [{"url": asset.browser_download_url}],
    }


def main() -> None:
    rel = fetch_latest_release()
    platform_descriptors = {
        platform: platform_descriptor(platform, find_asset_for_platform(rel, platform))
        for platform in PLATFORMS.keys()
    }
    descriptor = {
        "name": f"cpython-{PYTHON_VERSION}",
        "platforms": platform_descriptors,
    }
    print("#!/usr/bin/env dotslash")
    print()
    print(json.dumps(descriptor, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
