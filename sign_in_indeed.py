"""
sign_in_indeed.py
=================
Standalone script to sign into Indeed via Google OAuth using Playwright.

- Loads credentials from  backend/.env  (GOOGLE_EMAIL, GOOGLE_PASSWORD)
- Saves/reuses the browser session in  backend/data/auth_state.json
- Run from the repo root:
    python sign_in_indeed.py
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright.async_api import TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR       = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR    = os.path.join(ROOT_DIR, "backend")
ENV_PATH       = os.path.join(BACKEND_DIR, ".env")
AUTH_STATE_PATH = os.path.join(BACKEND_DIR, "data", "auth_state.json")

load_dotenv(ENV_PATH)

GOOGLE_EMAIL    = os.environ.get("GOOGLE_EMAIL", "")
GOOGLE_PASSWORD = os.environ.get("GOOGLE_PASSWORD", "")
INDEED_BASE     = "https://www.indeed.com"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Google OAuth helper
# ---------------------------------------------------------------------------
async def _sign_in_google(page: Page) -> None:
    """Click the Google sign-in button on Indeed and complete the OAuth flow."""
    logger.info("Starting Google sign-in flow...")

    google_btn_selectors = [
        "button[data-tn-element='google']",
        "a[data-tn-element='google']",
        "button[aria-label*='Google']",
        "a[aria-label*='Google']",
    ]

    google_page = None
    for sel in google_btn_selectors:
        el = await page.query_selector(sel)
        if el:
            try:
                async with page.expect_popup(timeout=8_000) as popup_info:
                    await el.click()
                google_page = await popup_info.value
                logger.info("Google popup opened.")
            except PWTimeout:
                google_page = page
                logger.info("No popup detected — using same tab.")
            break

    # Fallback: search all frames for any link/button containing "Google"
    if google_page is None:
        for frame in page.frames:
            els = await frame.query_selector_all("a, button")
            for el in els:
                txt = (await el.inner_text()).strip().lower()
                if "google" in txt:
                    try:
                        async with page.expect_popup(timeout=8_000) as popup_info:
                            await el.click()
                        google_page = await popup_info.value
                    except PWTimeout:
                        google_page = page
                    break
            if google_page:
                break

    if google_page is None:
        logger.warning("Could not find Google sign-in button — aborting.")
        return

    await google_page.wait_for_load_state("domcontentloaded")
    logger.info("Google page URL: %s", google_page.url)

    # Enter email
    try:
        await google_page.wait_for_selector("input[type=email]", timeout=15_000)
        await google_page.fill("input[type=email]", GOOGLE_EMAIL)
        await google_page.press("input[type=email]", "Enter")
        logger.info("Email entered.")
    except PWTimeout:
        logger.warning("Email input not found.")
        return

    # Enter password
    try:
        await google_page.wait_for_selector("input[type=password]", timeout=15_000)
        await asyncio.sleep(1)
        await google_page.fill("input[type=password]", GOOGLE_PASSWORD)
        await google_page.press("input[type=password]", "Enter")
        logger.info("Password entered.")
    except PWTimeout:
        logger.warning("Password input not found.")
        return

    # Wait for redirect back to Indeed
    logger.info("Waiting for redirect back to Indeed (up to 90s)...")
    try:
        await google_page.wait_for_url("*indeed.com*", timeout=90_000)
        logger.info("Back on Indeed — login complete.")
    except PWTimeout:
        logger.warning("Did not redirect to Indeed within 90s.")
    except Exception as exc:
        if "closed" in str(exc).lower() or "target" in str(exc).lower():
            logger.info("Popup closed after OAuth redirect — login complete.")
        else:
            logger.warning("Unexpected error waiting for redirect: %s", exc)

    await asyncio.sleep(3)


# ---------------------------------------------------------------------------
# Main login check
# ---------------------------------------------------------------------------
async def ensure_logged_in(context: BrowserContext) -> None:
    """
    Navigate to Indeed; run Google OAuth if not already authenticated.
    Persists the session to AUTH_STATE_PATH on success.
    """
    page = await context.new_page()
    await page.goto(INDEED_BASE, wait_until="domcontentloaded", timeout=30_000)
    await asyncio.sleep(3)

    url = page.url
    logger.info("Indeed landing URL: %s", url)

    needs_login = (
        "sign" in url.lower()
        or "login" in url.lower()
        or await page.query_selector("input[name=email][type=email]") is not None
    )

    if needs_login:
        logger.info("Login required — starting Google OAuth flow.")
        await _sign_in_google(page)
        try:
            await page.wait_for_url("*indeed.com*", timeout=15_000)
        except Exception:
            pass
        await asyncio.sleep(3)
        await context.storage_state(path=AUTH_STATE_PATH)
        logger.info("Auth state saved to %s", AUTH_STATE_PATH)
    else:
        logger.info("Already authenticated — no login needed.")

    await page.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        logger.error(
            "GOOGLE_EMAIL / GOOGLE_PASSWORD not set. "
            "Make sure backend/.env exists and contains both variables."
        )
        sys.exit(1)

    logger.info("Auth state path: %s", AUTH_STATE_PATH)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )

        ctx_kwargs = dict(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        # Reuse existing session if available
        if os.path.exists(AUTH_STATE_PATH):
            ctx_kwargs["storage_state"] = AUTH_STATE_PATH
            logger.info("Loaded existing auth state from %s", AUTH_STATE_PATH)

        context = await browser.new_context(**ctx_kwargs)
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        await ensure_logged_in(context)
        await browser.close()

    logger.info("Done.")


if __name__ == "__main__":
    asyncio.run(main())
