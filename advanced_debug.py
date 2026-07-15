import asyncio
from playwright.async_api import async_playwright
import os
import sys

# Add path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def debug_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Visual debugging
        page = await browser.new_page()
        
        print(f"Navigating to {config.PORTAL_URL}...")
        await page.goto(config.PORTAL_URL)
        
        try:
            # Wait for email field
            await page.wait_for_selector("input#login_id", timeout=20000)
            print(f"Typing email: {config.ZOHO_USERNAME}")
            await page.fill("input#login_id", config.ZOHO_USERNAME)
            await page.click("button#nextbtn")
            
            # Wait for password
            await page.wait_for_selector("input#password", timeout=10000)
            print("Typing password...")
            await page.fill("input#password", config.ZOHO_PASSWORD)
            await page.click("button#nextbtn")
            
            # Wait a bit for transition
            await asyncio.sleep(10)
            
            # Capture what happened
            screenshot_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\post_login_debug.png"
            await page.screenshot(path=screenshot_path)
            print(f"Post-login screenshot saved to {screenshot_path}")
            print(f"Final URL: {page.url}")
            
        except Exception as e:
            print(f"Debug failed: {e}")
            await page.screenshot(path=r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\error_screenshot.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login())
