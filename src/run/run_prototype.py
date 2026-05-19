from __future__ import annotations

from run._bootstrap import ensure_src_path

ensure_src_path()

from scripts.prototype.cli import main

if __name__ == "__main__":
    main()
