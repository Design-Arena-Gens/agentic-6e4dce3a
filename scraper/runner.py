from __future__ import annotations
import os
import random
import string
import concurrent.futures
from pathlib import Path
from typing import Any, Dict, List

from .config import (
    ProxyConfig,
    CONCURRENT_SESSIONS,
    MIN_PAGES_PER_SESSION,
    MAX_PAGES_PER_SESSION,
    OUTPUT_DIR,
)
from .urls import choose_random_urls
from .utils import ensure_dir, ts, write_json
from .pw_fallback import run_pw_session


def _rand_id(prefix: str) -> str:
    return f"{prefix}-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def _make_proxy_dict(cfg: ProxyConfig) -> Dict[str, Any]:
    return {"host": cfg.host, "port": cfg.port, "username": cfg.username, "password": cfg.password}


def _run_single_session(idx: int, proxy: Dict[str, Any], base_out: Path) -> Dict[str, Any]:
    n_pages = random.randint(MIN_PAGES_PER_SESSION, MAX_PAGES_PER_SESSION)
    urls = choose_random_urls(n_pages)
    sid = _rand_id(f"s{idx}")
    out_dir = ensure_dir(base_out)

    disable_uc = os.getenv("DISABLE_UC", "false").lower() in ("1", "true", "yes")
    if not disable_uc:
        # Import lazily to avoid heavy deps when UC is disabled or unavailable
        from .uc_selenium import run_uc_session  # type: ignore
        # Try undetected-chromedriver first
        result = run_uc_session(sid, urls, proxy, out_dir)
        if result.get("ok"):
            return result

    # Fallback to Playwright
    fallback = run_pw_session(sid, urls, proxy, out_dir)
    return fallback


def run_all() -> Dict[str, Any]:
    proxy_cfg = ProxyConfig.from_env()
    proxy = _make_proxy_dict(proxy_cfg)

    base_out = ensure_dir(Path(OUTPUT_DIR) / f"run-{ts()}")

    sessions: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_SESSIONS) as ex:
        futs = [ex.submit(_run_single_session, i + 1, proxy, base_out) for i in range(CONCURRENT_SESSIONS)]
        for f in concurrent.futures.as_completed(futs):
            sessions.append(f.result())

    summary = {
        "ok": any(s.get("ok") for s in sessions),
        "concurrent_sessions": CONCURRENT_SESSIONS,
        "sessions": sessions,
        "output_dir": str(base_out),
    }
    write_json(base_out / "summary.json", summary)
    return summary
