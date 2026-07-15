import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def find_hours():
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
        
        await page.wait_for_selector("#zp_maintab_timetracker", timeout=60000)
        await page.click("#zp_maintab_timetracker")
        await page.wait_for_selector("button#addtimelogbutton", timeout=30000)
        await page.click("button#addtimelogbutton")
        await asyncio.sleep(5)
        
        # Look for inputs related to time or hours
        inputs = await page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('input').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    results.push({
                        tag: el.tagName,
                        id: el.id,
                        name: el.name,
                        class: el.className,
                        placeholder: el.placeholder,
                        value: el.value,
                        type: el.type
                    });
                }
            });
            return results;
        }""")
        
        print("Visible Inputs:")
        for i in inputs:
            print(i)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_hours())
