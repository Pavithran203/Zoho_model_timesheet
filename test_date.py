import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser.browser_setup import BrowserManager
from browser.login_handler import LoginHandler
from browser.navigator import Navigator

async def test_date_fill():
    browser_mgr = BrowserManager()
    page = await browser_mgr.start()
    
    login_h = LoginHandler(page)
    await login_h.login()
    
    navigator = Navigator(page)
    await navigator.to_timesheet()
    
    await page.goto("https://people.zoho.in/group10/zp#timetracker/mydata/timelogs-mode:list")
    await page.wait_for_selector("#addtimelogbutton", timeout=15000)
    await asyncio.sleep(1)
    
    await page.click("#addtimelogbutton", timeout=5000)
    await asyncio.sleep(2)
    
    # Handle location popup
    try:
        allow_btn = page.locator("button:has-text('Allow'), button:has-text('allow this time'), button:has-text('Allow this time')").filter(visible=True).first
        if await allow_btn.count() > 0:
            await allow_btn.click()
            print("Clicked 'Allow this time' popup")
            await asyncio.sleep(1)
    except Exception:
        pass
    
    date_container = page.locator("div[folabel='Date']").filter(visible=True).first
    date_el = date_container.locator("input.zinputfield__textbox").first
    
    # Today is 06-03-2026, target is 02-03-2026
    # Test A: triple-click + type ONLY 8 digits (no dashes)
    # From the previous test: typing "02032026" gave "20-03-2026"
    # This means month gets 2 digits from day segment overflow
    # Let's try triple click + delay between segments
    
    print("Test A: Triple-click, then type day, wait, month, wait, year")
    await date_el.click(click_count=3)
    await asyncio.sleep(0.3)
    
    # Type day
    await page.keyboard.type("02", delay=150)
    await asyncio.sleep(0.5) # Wait for mask to advance
    
    # Type month
    await page.keyboard.type("03", delay=150)
    await asyncio.sleep(0.5)
    
    # Type year
    await page.keyboard.type("2026", delay=150)
    await asyncio.sleep(0.5)
    
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.3)

    val_a = await page.evaluate("""() => {
        const c = document.querySelector("div[folabel='Date']");
        if (c) { const inp = c.querySelector("input.zinputfield__textbox"); if (inp) return inp.value; }
        return 'Not Found';
    }""")
    print(f"Result A: '{val_a}'")
    
    # Close form
    await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    
    # Reopen form for Test B
    await page.click("#addtimelogbutton", timeout=5000)
    await asyncio.sleep(2)
    
    date_container2 = page.locator("div[folabel='Date']").filter(visible=True).first
    date_el2 = date_container2.locator("input.zinputfield__textbox").first
    
    # Test B: Click on the calendar icon, pick the date from the calendar
    print("Test B: Click calendar icon approach")
    cal_icon = date_container2.locator(".zdatetimefield__iconlabel, .zdatetimefield__icon").first
    await cal_icon.click()
    await asyncio.sleep(1)
    
    # Look for the calendar day cells
    day_cells = await page.evaluate("""() => {
        const results = [];
        document.querySelectorAll('[class*="calendar"] td, [class*="picker"] td, [class*="Calendar"] td').forEach(td => {
            if (td.offsetParent !== null) {
                results.push({text: td.innerText.trim(), class: td.className, id: td.id});
            }
        });
        return results;
    }""")
    print(f"Calendar day cells found: {len(day_cells)}")
    if day_cells:
        for c in day_cells[:10]:
            print(f"  {c}")
    
    await page.screenshot(path="calendar_open.png", full_page=True)
    
    # Try clicking day "2" in the calendar
    try:
        day2 = page.locator("[class*='calendar'] td, [class*='picker'] td").filter(has_text="2").first
        await day2.click()
        await asyncio.sleep(0.5)
        print("Clicked day 2 in calendar")
    except Exception as e:
        print(f"Calendar click failed: {e}")
    
    val_b = await page.evaluate("""() => {
        const c = document.querySelector("div[folabel='Date']");
        if (c) { const inp = c.querySelector("input.zinputfield__textbox"); if (inp) return inp.value; }
        return 'Not Found';
    }""")
    print(f"Result B: '{val_b}'")

    await page.screenshot(path="date_test_result.png", full_page=True)
    await browser_mgr.stop()

if __name__ == "__main__":
    asyncio.run(test_date_fill())
