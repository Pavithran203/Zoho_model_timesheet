import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser.browser_setup import BrowserManager
from browser.login_handler import LoginHandler
from browser.navigator import Navigator
from modules.worklog_updater import WorkLogUpdater
import time

async def test_date_fill():
    browser_mgr = BrowserManager()
    page = await browser_mgr.start()
    
    login_h = LoginHandler(page)
    await login_h.login()
    
    navigator = Navigator(page)
    await navigator.to_timesheet()
    
    updater = WorkLogUpdater(page)
    await updater.page.goto("https://people.zoho.in/group10/zp#timetracker/mydata/timelogs-mode:list")
    await asyncio.sleep(2) 
    
    # Open Form
    add_sel = "button:has-text('Log Time'), .ztp_log_time_btn, #addtimelogbutton, .zpl_addbtn"
    try:
        await updater.page.click(add_sel, timeout=4000)
    except:
        await updater.page.click(".zp_add_icon, .zicon-plus, button.zp_btn_primary", timeout=2000)

    await asyncio.sleep(1) 
    
    date_info = await updater.page.evaluate("""() => {
        let results = [];
        document.querySelectorAll('label').forEach(lbl => {
            if (lbl.innerText.includes('Date')) {
                let p = lbl.parentElement.parentElement;
                let inp = p.querySelector('input');
                if (inp) {
                    results.push({html: inp.outerHTML, class: inp.className, parent: p.innerHTML});
                }
            }
        });
        return results;
    }""")
    print("DATE FIELD INFO:")
    print(date_info)
    
    await browser_mgr.stop()

if __name__ == "__main__":
    asyncio.run(test_date_fill())
