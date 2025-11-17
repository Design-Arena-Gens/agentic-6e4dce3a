from __future__ import annotations
import json
from pathlib import Path

from scraper.runner import run_all
from scraper.utils import ensure_dir


def main() -> None:
    summary = run_all()
    # Also emit a public data.json for the web app
    web_public = ensure_dir(Path("web/public"))
    with (web_public / "data.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
