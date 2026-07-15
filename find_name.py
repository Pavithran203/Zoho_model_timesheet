import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def find_name():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(config.PORTAL_URL)
        await page.wait_for_selector("input#login_id")
        await page.fill("input#login_id", config.ZOHO_USERNAME)
        await page.click("button#nextbtn")
        await page.wait_for_selector("input#password")
        await page.fill("input#password", config.ZOHO_PASSWORD)
        await page.click("button#nextbtn")
        
        await page.wait_for_selector(".zp-dashboard, .zpeople-home, .zp-left-nav, .nav_container", timeout=60000)
        
        # Look for the name "Ramalingam Pavithran"
        selectors = await page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.innerText && el.innerText.includes('Ramalingam Pavithran')) {
                    if (el.children.length === 0) { // Only leaf nodes
                        results.push({
                            tag: el.tagName,
                            id: el.id,
                            class: el.className,
                            text: el.innerText.trim()
                        });
                    }
                }
            });
            return results;
        }""")
        
        print("Candidate Name Selectors:")
        for s in selectors:
            print(s)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_name())
