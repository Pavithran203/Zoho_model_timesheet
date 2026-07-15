from playwright.async_api import Page
from utils.logger import logger
import config
import asyncio

class Navigator:
    def __init__(self, page: Page):
        self.page = page

    async def to_attendance(self):
        """Navigate to Attendance/Shift section."""
        logger.log_event("Navigating to Attendance module...")
        try:
            # India Portal uses #zp_maintab_attendance
            await self.page.click("#zp_maintab_attendance, li#m_attendance, a:has-text('Attendance')", timeout=10000)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2) # Reduced from 5s
            logger.log_event("Attendance section loaded.")
            return True
        except:
            logger.log_event("Retrying navigation via URL...", level="warning")
            target = "https://people.zoho.in/group10/zp#attendance/entry/summary-mode:list"
            await self.page.goto(target, wait_until="networkidle")
            await asyncio.sleep(3) # Reduced from 8s
            return True

    async def to_timesheet(self):
        """Navigate to Work Log/Timesheet section."""
        logger.log_event("Navigating to Timesheet module...")
        try:
            # India Portal uses #zp_maintab_timetracker for Time Tracker
            await self.page.click("#zp_maintab_timetracker, li#m_timesheet, a:has-text('Time Tracker')", timeout=10000)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2) # Reduced from 5s
            return True
        except:
            target = "https://people.zoho.in/group10/zp#timetracker/mydata/timelogs-mode:list"
            await self.page.goto(target, wait_until="networkidle")
            await asyncio.sleep(3) # Reduced from 8s
            return True
