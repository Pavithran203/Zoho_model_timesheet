import asyncio
from playwright.async_api import Page
from utils.logger import logger
from datetime import datetime

class DataExtractor:
    def __init__(self, page: Page):
        self.page = page

    async def get_attendance_data(self):
        """Module 4: Extraction of shift and attendance status."""
        logger.log_event("Extracting employee and shift data...")
        # Smart wait instead of 5s fixed sleep
        try:
            await self.page.wait_for_selector(".zp-user-name, .zp-attendance, .zp_attendance_time", timeout=5000)
        except:
            pass
        await asyncio.sleep(1) 
        
        data = {
            "employee_name": "Unknown",
            "attendance_status": "Unknown",
            "shift_start": "09:00",
            "shift_end": "18:00",
            "current_time": datetime.now().strftime("%H:%M"),
            "timesheet_status": "Pending"
        }

        try:
            # 1. Employee Name: More thorough detection
            name_selectors = [
                "b.zpl_link", ".zp-user-name", "#zp_user_name", 
                ".user-name", ".zp-ms-name", ".zp-profile-name",
                ".top-nav-user-name", ".zp-user-avatar + span"
            ]
            for sel in name_selectors:
                try:
                    el = await self.page.query_selector(sel)
                    if el and await el.is_visible():
                        name = (await el.inner_text()).strip()
                        if name and name.lower() != "unknown":
                            data["employee_name"] = name
                            break
                except:
                    continue

            # 2. Attendance Status: More robust detection
            # We look for the status indicator text first
            status_text = await self.page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('.zp-checkin-status, .attendance-status, .zpl_link, .zp-status-text'));
                for (let el of els) {
                    const txt = el.innerText;
                    if (txt.includes('Checked-in') || txt.includes('Checked in')) return 'Checked in';
                    if (txt.includes('Checked-out') || txt.includes('Checked out')) return 'Checked out';
                    if (txt.includes('Weekend') || txt.includes('Holiday')) return 'Weekend / Off';
                }
                return '';
            }""")
            
            if status_text:
                data["attendance_status"] = status_text
            else:
                # Fallback: check for button specific presence
                try:
                    # If CHECK-OUT button is visible, user IS checked-in
                    btn_checkout = self.page.locator("button:has-text('Check-out'), .zp-checkout-btn").filter(visible=True)
                    if await btn_checkout.count() > 0:
                        data["attendance_status"] = "Checked in"
                    else:
                        btn_checkin = self.page.locator("button:has-text('Check-in'), .zp-checkin-btn").filter(visible=True)
                        if await btn_checkin.count() > 0:
                            data["attendance_status"] = "Checked out"
                        elif await self.page.locator("text=Weekend, text=Off").filter(visible=True).count() > 0:
                            data["attendance_status"] = "Weekend / Off"
                        else:
                            data["attendance_status"] = "Checked out" # Safe default
                except:
                    data["attendance_status"] = "Checked out"

            # Detect Shift Timings (Refine with actual layout)
            shift_info = await self.page.query_selector(".shift-timing")
            if shift_info:
                timing = await shift_info.inner_text()
                if "-" in timing:
                    data["shift_end"] = timing.split("-")[-1].strip()

            logger.log_event(f"Extracted: Name={data['employee_name']}, Status={data['attendance_status']}, End={data['shift_end']}")
            return data

        except Exception as e:
            logger.log_event(f"Extraction partial failure: {str(e)}", level="warning")
            return data
