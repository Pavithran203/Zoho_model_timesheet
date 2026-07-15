from playwright.async_api import Page
from utils.logger import logger
from datetime import datetime

class LogoutExecutor:
    def __init__(self, page: Page):
        self.page = page

    async def execute_checkout(self):
        """Module 6: Perform Logout/Check-out."""
        logger.log_event("Attempting to perform Check-out...")
        try:
            # Click Check-out button (Handle confirmations)
            checkout_btn = await self.page.get_by_text("Check-out", exact=False).first
            if await checkout_btn.is_visible():
                await checkout_btn.click()
                await self.page.wait_for_timeout(2000) # Wait for processing
                
                # Check for confirmation modals
                confirm_btn = await self.page.query_selector("button:has-text('Confirm'), button:has-text('Yes')")
                if confirm_btn:
                    await confirm_btn.click()
                
                logger.log_event("Check-out button clicked successfully.")
                return True
            else:
                logger.log_event("Check-out button not found or already logged out.")
                return False
        except Exception as e:
            logger.log_event(f"Check-out execution failed: {str(e)}", level="error")
            return False

    async def sign_out_system(self):
        """Perform full system sign-out."""
        logger.log_event("Performing system Sign-out...")
        try:
            await self.page.click("#user_info_avatar, .zp-user-avatar")
            await self.page.click("text=Sign Out")
            logger.log_event("System sign-out completed.")
            return True
        except:
            return False
        
    async def get_summary(self, status):
        return {
            "logout_status": "Success" if status else "Failed",
            "logout_time": datetime.now().strftime("%H:%M:%S")
        }
