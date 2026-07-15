import asyncio
from playwright.async_api import async_playwright
import os

async def capture_state():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://people.zoho.com/"
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(5) # Wait for redirects
            
            # Save screenshot to artifacts (use the path provided in the context)
            screenshot_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\login_debug.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Print page title and current URL
            print(f"Current URL: {page.url}")
            print(f"Page Title: {page.title()}")
            
            # Check for selectors
            selectors = ["input#login_id", "input#password", ".zp-dashboard", ".zpeople-home", "iframe"]
            for s in selectors:
                found = await page.query_selector(s)
                print(f"Selector '{s}' found: {found is not None}")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_state())
