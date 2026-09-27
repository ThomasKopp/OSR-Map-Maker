"""Run PyInstaller with a deterministic home directory for profile-less CI hosts.

Normal Windows desktop installations provide a user profile.  Some headless
automation hosts do not, while PyInstaller consults ``Path.home()`` during
Windows DLL filtering.  This bootstrap only affects the build subprocess and
keeps its temporary profile under the configured build work directory.
"""
from __future__ import annotations

import os
import pathlib
from pathlib import Path


def main() -> None:
    build_home = Path(os.environ.get("OSR_MAP_BUILD_HOME", "build/pyinstaller-home"))
    build_home.mkdir(parents=True, exist_ok=True)
    pathlib.Path.home = classmethod(lambda _cls: build_home.resolve())  # type: ignore[method-assign]

    from PyInstaller.__main__ import run

    run()


if __name__ == "__main__":
    main()
