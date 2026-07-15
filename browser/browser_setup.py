from playwright.async_api import async_playwright
import config
from utils.logger import logger

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """Module 1: Browser Initialization."""
        logger.log_event("Initializing browser (Chromium)...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=config.HEADLESS,
            args=["--start-maximized"]
        )
        # Create context with a larger viewport and grant location
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            geolocation={"longitude": 80.2707, "latitude": 13.0827}, # Chennai default
            permissions=["geolocation"]
        )
        self.page = await self.context.new_page()
        logger.log_event("Browser launched successfully.")
        return self.page

    async def stop(self):
        """Safely close everything."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.log_event("Browser closed safely.")
