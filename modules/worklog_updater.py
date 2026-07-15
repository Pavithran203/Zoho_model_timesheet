import random
from datetime import datetime, timedelta
from playwright.async_api import Page
from utils.logger import logger
import asyncio

class WorkLogUpdater:
    def __init__(self, page: Page):
        self.page = page

    async def select_dropdown_option(self, container_selector, target_text):
        """Select a specific option from a Zoho zselectbox dropdown."""
        try:
            container = self.page.locator(container_selector).filter(visible=True).first
            if await container.count() > 0:
                await container.click()
                await asyncio.sleep(0.5)
                options = self.page.locator(
                    "li.zselectbox__option, .zdropdownlist__item, .zpl_slli"
                ).filter(visible=True)
                count = await options.count()
                all_texts = []
                for i in range(count):
                    text = await options.nth(i).inner_text()
                    all_texts.append(text.strip())
                    if target_text.lower() in text.lower():
                        await options.nth(i).click()
                        logger.log_event(f"Selected '{target_text}' in {container_selector}.")
                        await asyncio.sleep(0.5)
                        return True
                logger.log_event(f"Available options in {container_selector}: {all_texts}", level="warning")
                # Fallback: pick first real option
                if count > 1:
                    await options.nth(1).click()
                    logger.log_event(f"Fallback selected '{all_texts[1] if len(all_texts)>1 else 'first'}' in {container_selector}.")
                    return True
        except Exception as e:
            logger.log_event(f"Dropdown error on {container_selector}: {e}", level="warning")
        return False

    async def get_logged_dates(self):
        """Scrape the log list to find dates already submitted with thorough scrolling."""
        logger.log_event("Checking existing logs to avoid duplicates...")
        try:
            # Thorough scroll to trigger lazy loading
            await self.page.evaluate("""() => {
                const list = document.querySelector('.ztime-log-list, .zpl_list, #ztime-log-list');
                if (list) {
                    list.scrollTop = list.scrollHeight;
                }
                window.scrollTo(0, document.body.scrollHeight);
            }""")
            await asyncio.sleep(2) # Reduced from 3s

            # Scrape using a more global search on body innerText
            dates = await self.page.evaluate(r"""() => {
                const results = [];
                const monthMap = { 
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 
                    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                };
                
                // 1. Try to find the currently displayed month/year on the page (e.g. "March 2026")
                let pageMonth = new Date().getMonth() + 1;
                let pageYear = new Date().getFullYear();
                const headers = document.body.innerText.match(/(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}/i);
                if (headers) {
                    const hParts = headers[0].split(/\s+/);
                    pageMonth = monthMap[hParts[0].toLowerCase().substring(0, 3)];
                    pageYear = hParts[1];
                }

                const dateRegex = /(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(\w{3}\s\d{1,2},\s\d{4})|(\d{1,2}\s\w{3}\s\d{4})|(\d{1,2}\s\w{3})|(\w{3}\s\d{1,2})/g;

                const normalizeDate = (d) => {
                    const parts = d.replace(',', '').split(/\s+|-|\//);
                    if (parts.length < 2) return null;
                    
                    let day, monthStr, year = pageYear;
                    
                    // Logic to handle "Mar 02", "02 Mar", "02-03-2026", etc.
                    if (isNaN(parts[0])) { // Starts with text: "Mar 02"
                        monthStr = parts[0].toLowerCase().substring(0, 3);
                        day = parts[1];
                        if (parts[2]) year = parts[2];
                    } else { // Starts with number: "02 Mar" or "02-01-26"
                        day = parts[0];
                        monthStr = parts[1].toLowerCase().substring(0, 3);
                        if (parts[2]) year = parts[2];
                    }
                    
                    let m = monthMap[monthStr] || ( !isNaN(monthStr) ? monthStr.padStart(2, '0') : pageMonth.toString().padStart(2, '0') );
                    if (!m) return null;
                    if (m.toString().length === 1) m = '0' + m;
                    
                    if (year.toString().length === 2) year = '20' + year;
                    return `${day.toString().padStart(2, '0')}-${m}-${year}`;
                };

                // Search ONLY within log containers to avoid false positives from headers/footers
                const container = document.querySelector('.ztime-log-list, .zpl_list, #ztime-log-list, .zpl_list_container');
                const searchArea = container ? container.innerText : '';
                
                const matches = searchArea.match(dateRegex);
                if (matches) {
                    matches.forEach(m => {
                        const norm = normalizeDate(m);
                        if (norm) results.push(norm);
                    });
                }
                
                return results;
            }""")
            unique_dates = list(set(dates))
            logger.log_event(f"Detected existing entries for: {unique_dates}")
            return unique_dates
        except Exception as e:
            logger.log_event(f"Failed to check existing logs: {e}", level="warning")
            return []

    async def submit_weekly_logs(self):
        """Submit Mon–Fri logs for the current week, skipping existing entries."""
        logger.log_event("=== Starting weekly work log submission ===")

        # Navigate to Time Tracker → Time Logs view
        await self.page.goto(
            "https://people.zoho.in/group10/zp#timetracker/mydata/timelogs-mode:list"
        )
        await asyncio.sleep(3) # Reduced from 10s

        # Ensure "Time Logs" sub-tab is active
        try:
            await self.page.click("text=Time Logs, #m_timelogs", timeout=5000)
            await asyncio.sleep(5)
        except:
            pass

        # Check existing logs
        existing_logs = await self.get_logged_dates()

        now = datetime.now()
        monday = now - timedelta(days=now.weekday())

        tasks = [
            "Project coordination, task tracking, and module development.",
            "Database optimization, query tuning, and performance review.",
            "Technical documentation, API testing, and integration checks.",
            "Bug fixing, security patch validation, and QA verification.",
            "UI/UX review, front-end integration, and deployment support.",
        ]

        for i in range(5):  # Mon = 0 … Fri = 4
            log_date_dt = monday + timedelta(days=i)
            if log_date_dt.date() > now.date():
                continue

            # Standard for matching (dd-mm-yyyy)
            log_date_str = log_date_dt.strftime("%d-%m-%Y")
            # Zoho datepicker format is dd-mm-yyyy (e.g. 04-03-2026)
            zoho_date_str = log_date_dt.strftime("%d-%m-%Y")
            
            if log_date_str in existing_logs:
                logger.log_event(f"SKIPPING: Log already exists for {log_date_str}")
                continue

            work_hours = f"08:{random.randint(0, 30):02d}"
            description = tasks[i % len(tasks)]

            logger.log_event(f"--- Day {i+1}: {log_date_str} ({zoho_date_str}) | {work_hours} ---")
            ok = await self.submit_single_log(zoho_date_str, work_hours, description)
            logger.log_event(
                f"{'SUBMITTED' if ok else 'FAILED'}: {log_date_str}",
                level="info" if ok else "error"
            )
            
            if ok:
                existing_logs.append(log_date_str)
            
            await asyncio.sleep(1)

        return True

    async def submit_single_log(self, log_date: str, hours: str, summary: str) -> bool:
        """Open form and fill in exact requested order: Client -> Project -> Job -> Work Item -> Date -> Description."""
        try:
            # Quick check to skip re-nav if already on list
            if not self.page.url.endswith("timelogs-mode:list"):
                await self.page.goto("https://people.zoho.in/group10/zp#timetracker/mydata/timelogs-mode:list")
                await asyncio.sleep(2) 
            
            # ── Step 1: Open Form ──────────────────────────────────────────────
            add_sel = "button:has-text('Log Time'), .ztp_log_time_btn, #addtimelogbutton, .zpl_addbtn"
            try:
                await self.page.click(add_sel, timeout=4000)
            except:
                await self.page.click(".zp_add_icon, .zicon-plus, button.zp_btn_primary", timeout=2000)

            await asyncio.sleep(1.5) 

            # ── Step 1b: Handle Location / "Allow this time" popup ──────────────
            try:
                allow_btn = self.page.locator("button:has-text('Allow'), button:has-text('allow this time'), button:has-text('Allow this time')").filter(visible=True).first
                if await allow_btn.count() > 0:
                    await allow_btn.click()
                    logger.log_event("Clicked 'Allow this time' location popup.")
                    await asyncio.sleep(1)
            except Exception:
                pass

            # ── Helper for Smart Fill ──────────────────
            async def is_field_filled(container_selector):
                try:
                    text = await self.page.locator(f"{container_selector} .zselectbox__text").inner_text()
                    return text and text.strip().lower() not in ["", "select", "-select-", "none"]
                except:
                    return False

            # ── Step 2-4: Dropdowns (Client -> Project -> Job) ──────────────────
            # Step 2: Client
            if await is_field_filled("#timelogClient-container"):
                logger.log_event("Client field already filled, skipping.")
            else:
                await self.select_dropdown_option("#timelogClient-container", "In-house")

            # Step 3: Project
            if await is_field_filled("#timelogProject-container"):
                logger.log_event("Project field already filled, skipping.")
            else:
                await self.select_dropdown_option("#timelogProject-container", "Digital internal")

            # Step 4: Job
            if await is_field_filled("#timelogJob-container"):
                logger.log_event("Job field already filled, skipping.")
            else:
                await self.select_dropdown_option("#timelogJob-container", "Learning")

            # ── Step 5: Work Item ───────────────────────────────────────────────
            work_item = self.page.locator("input[name='Work_Item'], [id^='zp_field_'][name='Work_Item']").filter(visible=True).first
            if await work_item.count() > 0:
                # Check if already has value
                current_val = await work_item.input_value()
                if not current_val:
                    await work_item.fill("Technical Learning & Development")
                    await work_item.press("Enter")
                    logger.log_event("Filled Work Item.")
                else:
                    logger.log_event(f"Work Item already filled with: {current_val}")
            else:
                logger.log_event("Work Item field not found via standard locator", level="warning")

            # ── Step 6: Date & Hours ───────────────────────
            # Date - Zoho datepicker format is dd-mm-yyyy
            try:
                date_container = self.page.locator("div[folabel='Date'], div[folabel='date']").filter(visible=True).first
                date_el = date_container.locator("input.zinputfield__textbox").first
                if await date_el.count() > 0:
                    # Check if date is already correct to avoid unnecessary interaction
                    existing_date = await date_el.input_value()
                    if existing_date != log_date:
                        await date_el.click()
                        await asyncio.sleep(0.3)
                        for _ in range(15):
                            await self.page.keyboard.press("Backspace")
                            await self.page.keyboard.press("Delete")
                        for char in log_date:
                            await self.page.keyboard.press(char)
                            await asyncio.sleep(0.05)
                        await self.page.keyboard.press("Escape")
                        await date_el.press("Tab")
                        await asyncio.sleep(0.5)
                        logger.log_event(f"Date set to {log_date}")
                    else:
                        logger.log_event(f"Date already set to {log_date}")
            except Exception as e:
                logger.log_event(f"Date UI fill error: {e}", level="warning")
            
            # Hours
            hr_el = self.page.locator('#timelog_hrstime').filter(visible=True).first
            if await hr_el.count() > 0:
                current_hr = await hr_el.input_value()
                if current_hr != hours:
                    await hr_el.click()
                    for _ in range(5):
                        await self.page.keyboard.press("Backspace")
                        await self.page.keyboard.press("Delete")
                    for char in hours:
                        await self.page.keyboard.press(char)
                        await asyncio.sleep(0.05)
                    await hr_el.press("Enter")
                    logger.log_event(f"Hours set to {hours}")
                else:
                    logger.log_event(f"Hours already set to {hours}")

            # ── Step 7: Description ─────────────────────────────────────────────
            desc_el = self.page.locator("textarea[name='Description'], textarea.ztextbox").filter(visible=True).first
            if await desc_el.count() > 0:
                # Force fill even if not empty to ensure fresh daily description
                await desc_el.fill(summary)
                logger.log_event("Filled Description.")
            else:
                await self.page.evaluate(f"""(t) => {{
                    const el = document.querySelector("textarea[name='Description']") || document.querySelector("textarea.ztextbox");
                    if (el) {{ el.value = t; el.dispatchEvent(new Event('input', {{ bubbles: true }})); el.dispatchEvent(new Event('change', {{ bubbles: true }})); }}
                }}""", summary)

            # ── Step 8: Save ────────────────────────────────────────────────────
            save_sel = self.page.locator("button, .zbutton").filter(has_text="Save").filter(visible=True).first
            
            # Final verification of required fields before save
            # (In a real scenario, we'd check if internal state is valid, but here we just try to click)
            try:
                await save_sel.click(timeout=3000)
            except:
                await save_sel.click(force=True)
                
            logger.log_event(f"Form SAVE clicked for {log_date}")
            await asyncio.sleep(3) # Wait for submission feedback
            
            # Check for error messages on page
            error_toast = self.page.locator(".zmessage-error, .zpl_error, .error-msg").filter(visible=True)
            if await error_toast.count() > 0:
                err_text = await error_toast.first.inner_text()
                logger.log_event(f"Form submission error detected: {err_text}", level="error")
                return False

            return True

        except Exception as e:
            logger.log_event(f"Critical form error for {log_date}: {e}", level="error")
            await self.page.keyboard.press("Escape")
            return False
