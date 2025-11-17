from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        host = os.getenv("PROXY_HOST", "gw.dataimpulse.com")
        port = int(os.getenv("PROXY_PORT", "823"))
        username = os.getenv("PROXY_USER", "c147d949a38ca89c4c3a__cr.au,gb,us")
        password = os.getenv("PROXY_PASS", "b7351118825adfbd")
        return cls(host=host, port=port, username=username, password=password)


REAL_ESTATE_BASE = "https://www.realestate.com.au"
TARGET_SEED = os.getenv("TARGET_URL", f"{REAL_ESTATE_BASE}/vic/st-kilda-3182/")

# Concurrency controls
CONCURRENT_SESSIONS = int(os.getenv("CONCURRENT_SESSIONS", "3"))
MIN_PAGES_PER_SESSION = int(os.getenv("MIN_PAGES_PER_SESSION", "5"))
MAX_PAGES_PER_SESSION = int(os.getenv("MAX_PAGES_PER_SESSION", "20"))

# Timeouts
PAGE_LOAD_TIMEOUT_SEC = int(os.getenv("PAGE_LOAD_TIMEOUT_SEC", "40"))
TOTAL_SESSION_TIMEOUT_SEC = int(os.getenv("TOTAL_SESSION_TIMEOUT_SEC", "420"))

# Output
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "artifacts")
