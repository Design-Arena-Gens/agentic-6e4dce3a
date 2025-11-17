from __future__ import annotations
import random
import time
from pathlib import Path
from typing import Dict, List, Any

from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium_stealth import stealth

from .config import PAGE_LOAD_TIMEOUT_SEC


def _apply_stealth(driver: Chrome) -> None:
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )


def _get_chrome_options(user_agent: str | None = None) -> ChromeOptions:
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1200,900")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    # Headful by default (do not add --headless)
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    return options


def _rand_user_agent() -> str:
    uas = [
        # Popular stable desktop Chrome UAs (varying versions/platforms)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]
    return random.choice(uas)


def run_uc_session(
    session_id: str,
    urls: List[str],
    proxy: Dict[str, Any],
    out_dir: Path,
) -> Dict[str, Any]:
    """
    Attempts to browse a set of URLs using undetected-chromedriver + selenium-wire proxy + stealth.
    Returns session results with per-URL success flags and artifacts paths.
    """
    user_agent = _rand_user_agent()
    options = _get_chrome_options(user_agent)

    seleniumwire_options = {
        "proxy": {
            "http": f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
            "https": f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
            "no_proxy": "",
        },
        "verify_ssl": False,
        "timeout": PAGE_LOAD_TIMEOUT_SEC * 1000,
    }

    driver: Chrome | None = None
    results: List[Dict[str, Any]] = []

    try:
        driver = Chrome(options=options, seleniumwire_options=seleniumwire_options)
        _apply_stealth(driver)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SEC)

        for i, url in enumerate(urls, start=1):
            url_id = f"{i:02d}"
            item = {"url": url, "ok": False, "strategy": "uc", "html": None, "text_len": 0}
            try:
                driver.get(url)
                # Wait for body text to be present and non-trivial
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT_SEC).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(random.uniform(2.5, 5.5))

                body_text = driver.execute_script("return document.body && document.body.innerText || '';")
                title = driver.title or ""
                html = driver.page_source or ""
                text_len = len(body_text.strip())

                blocked = (
                    "429" in html[:1000] or
                    text_len < 400 or
                    title.strip() == ""
                )

                item.update({
                    "ok": not blocked,
                    "html": f"{session_id}_{url_id}.html",
                    "text_len": text_len,
                    "title": title,
                })

                # Save HTML snapshot regardless for inspection
                (out_dir / f"{session_id}_{url_id}.html").write_text(html, encoding="utf-8")

            except (TimeoutException, WebDriverException) as e:
                item.update({"error": str(e)})
            results.append(item)

    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

    session_ok = any(r.get("ok") for r in results)
    return {"session_id": session_id, "ok": session_ok, "results": results, "strategy": "uc"}
