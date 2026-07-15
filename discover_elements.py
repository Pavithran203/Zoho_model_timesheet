import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def discover_elements():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"Navigating to {config.PORTAL_URL}...")
        await page.goto(config.PORTAL_URL)
        
        try:
            await page.wait_for_selector("input#login_id", timeout=15000)
            await page.fill("input#login_id", config.ZOHO_USERNAME)
            await page.click("button#nextbtn")
            await page.wait_for_selector("input#password", timeout=10000)
            await page.fill("input#password", config.ZOHO_PASSWORD)
            await page.click("button#nextbtn")
            
            print("Password submitted. Waiting for transition (15s)...")
            await asyncio.sleep(15)
            
            # List some common div classes to find the sidebar
            elements = await page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('div, nav, li').forEach(el => {
                    if (el.className && typeof el.className === 'string' && el.className.includes('nav')) {
                        results.push({tag: el.tagName, class: el.className, text: el.innerText.substring(0, 20)});
                    }
                });
                return results.slice(0, 20);
            }""")
            print("Potential navigation elements found:")
            for el in elements:
                print(el)
                
            screenshot_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\discovery_screenshot.png"
            await page.screenshot(path=screenshot_path)
            
        except Exception as e:
            print(f"Discovery failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(discover_elements())
