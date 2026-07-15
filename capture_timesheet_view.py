import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def capture_timesheet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Logging in...")
        await page.goto(config.PORTAL_URL)
        await page.wait_for_selector("input#login_id")
        await page.fill("input#login_id", config.ZOHO_USERNAME)
        await page.click("button#nextbtn")
        await page.wait_for_selector("input#password")
        await page.fill("input#password", config.ZOHO_PASSWORD)
        await page.click("button#nextbtn")
        
        print("Waiting for Dashboard...")
        await page.wait_for_selector(".nav_container, .zp-left-nav", timeout=60000)
        
        print("Navigating to Time Tracker...")
        # Direct URL to avoid clicking issues
        await page.goto("https://people.zoho.in/group10/zp#timesheet/myspace/worklogs")
        await asyncio.sleep(15) # Strong wait for JS
        
        screenshot_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\final_timesheet_view.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_timesheet())
