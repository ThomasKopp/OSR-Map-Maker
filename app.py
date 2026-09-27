from __future__ import annotations

from osr_map_maker import OSRMapMaker

__all__ = ["OSRMapMaker"]


def main() -> None:
    app = OSRMapMaker()
    app.mainloop()


if __name__ == "__main__":
    main()
