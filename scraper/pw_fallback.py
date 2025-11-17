from __future__ import annotations
import asyncio
import random
from pathlib import Path
from typing import Dict, List, Any

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from .config import PAGE_LOAD_TIMEOUT_SEC


def _rand_user_agent() -> str:
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]
    return random.choice(uas)


import os


async def _run_playwright(session_id: str, urls: List[str], proxy: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    async with async_playwright() as p:
        headless = os.getenv("FORCE_HEADLESS", "false").lower() in ("1", "true", "yes")
        browser = await p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])  # headful under Xvfb (or headless if forced)
        context = await browser.new_context(
            user_agent=_rand_user_agent(),
            proxy={
                "server": f"http://{proxy['host']}:{proxy['port']}",
                "username": proxy["username"],
                "password": proxy["password"],
            },
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()
        await stealth_async(page)

        for i, url in enumerate(urls, start=1):
            url_id = f"{i:02d}"
            item = {"url": url, "ok": False, "strategy": "pw", "html": None, "text_len": 0}
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT_SEC * 1000)
                await page.wait_for_selector("body", timeout=PAGE_LOAD_TIMEOUT_SEC * 1000)
                await asyncio.sleep(random.uniform(2.0, 4.0))

                body_text = await page.evaluate("document.body && document.body.innerText || ''")
                title = await page.title()
                html = await page.content()

                text_len = len((body_text or "").strip())
                blocked = ("429" in html[:1000]) or (text_len < 400) or (not (title or "").strip())

                item.update({
                    "ok": not blocked,
                    "html": f"{session_id}_{url_id}.html",
                    "text_len": text_len,
                    "title": title,
                })
                (out_dir / f"{session_id}_{url_id}.html").write_text(html, encoding="utf-8")
            except Exception as e:
                item.update({"error": str(e)})
            results.append(item)

        await context.close()
        await browser.close()

    return {"session_id": session_id, "ok": any(r.get("ok") for r in results), "results": results, "strategy": "pw"}


def run_pw_session(session_id: str, urls: List[str], proxy: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    return asyncio.run(_run_playwright(session_id, urls, proxy, out_dir))
