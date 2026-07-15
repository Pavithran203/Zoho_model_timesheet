import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def analyze_form():
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
        
        # Navigate to Timesheet
        await page.click("#zp_maintab_timetracker")
        await asyncio.sleep(5)
        
        # Open Log Time form
        await page.click("button#addtimelogbutton")
        await asyncio.sleep(5)
        
        # Scan fields
        fields = await page.evaluate("""() => {
            const results = [];
            // Look for labels and their associated inputs
            document.querySelectorAll('label').forEach(label => {
                const text = label.innerText.trim();
                const input = label.nextElementSibling ? label.nextElementSibling.querySelector('input, textarea, select, .zselectbox, .zdropdownlist') : null;
                results.push({
                    labelText: text,
                    hasInput: !!input,
                    html: input ? input.outerHTML : 'N/A'
                });
            });
            
            // Also look for all inputs and their nearby text
            document.querySelectorAll('input, textarea, .zselectbox').forEach(el => {
               results.push({
                   tag: el.tagName,
                   id: el.id,
                   name: el.name,
                   class: el.className,
                   placeholder: el.placeholder,
                   type: el.type,
                   value: el.value
               });
            });
            return results;
        }""")
        
        print("FORMS FIELDS DISCOVERY:")
        for f in fields:
            print(f)
            
        await page.screenshot(path="form_discovery.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_form())
