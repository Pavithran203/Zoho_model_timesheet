import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

async def diagnose_timesheet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 1. Login
        print("Logging in...")
        await page.goto(config.PORTAL_URL)
        await page.wait_for_selector("input#login_id")
        await page.fill("input#login_id", config.ZOHO_USERNAME)
        await page.click("button#nextbtn")
        await page.wait_for_selector("input#password")
        await page.fill("input#password", config.ZOHO_PASSWORD)
        await page.click("button#nextbtn")
        
        # 2. Navigate to Timesheet
        print("Navigating to Timesheet...")
        # Wait for the main app container to load
        await page.wait_for_selector(".zp-main-container, .zpeople-home, .nav_container", timeout=60000)
        await page.click("li#m_timesheet, a:has-text('Time Tracker')")
        print("Waiting for page transition...")
        await asyncio.sleep(15) 
        
        # 3. List ALL clickable elements and buttons in the view
        print("Scanning for buttons...")
        elements = await page.evaluate("""() => {
            const items = [];
            document.querySelectorAll('button, a, .zp-plus-icon, [role="button"]').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    items.push({
                        tag: el.tagName,
                        text: el.innerText.trim(),
                        id: el.id,
                        class: el.className,
                        role: el.getAttribute('role')
                    });
                }
            });
            return items;
        }""")
        
        for item in elements:
            print(f"Found: {item}")
            
        screenshot_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\timesheet_diag.png"
        await page.screenshot(path=screenshot_path)
        print(f"Diagnostic screenshot saved to {screenshot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_timesheet())
