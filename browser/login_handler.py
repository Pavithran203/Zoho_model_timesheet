import config
import asyncio
from datetime import datetime
from utils.logger import logger
from playwright.async_api import Page

class LoginHandler:
    def __init__(self, page: Page):
        self.page = page

    async def dismiss_popups(self):
        """Helper to clear common Zoho overlays/popups."""
        popups = [
            "text=Upgrade", "text=Got it", "button:has-text('No thanks')",
            ".zp-close-icon", ".zpeople-dismiss", "text=Later",
            "button:has-text('Remind me later')"
        ]
        for selector in popups:
            try:
                btn = self.page.locator(selector).filter(visible=True).first
                if await btn.count() > 0:
                    await btn.click()
                    await asyncio.sleep(1)
            except:
                pass

    async def login(self):
        """Module 2: Secure Login Handler with Popup Resilience."""
        logger.log_event(f"Navigating to {config.PORTAL_URL}...")
        await self.page.goto(config.PORTAL_URL)
        
        try:
            # 1. Handle potential Marketing Page redirect
            if "zoho.com/people" in self.page.url:
                logger.log_event("Detected marketing landing page. Clicking Sign In...")
                await self.page.click("a.zh-login, text=Sign In", timeout=5000)
                await self.page.wait_for_load_state("networkidle")

            # 2. Wait for Login ID field or Dashboard
            # Expanded detection list
            detect_selectors = "input#login_id, .zp-dashboard, .zpeople-home, #password, .zp-attendance, #zp_maintab_attendance"
            await self.page.wait_for_selector(detect_selectors, timeout=config.TIMEOUT)
            
            if await self.page.query_selector("input#login_id"):
                logger.log_event("Performing credential-based login (Phase 1: Email)...")
                await self.page.fill("input#login_id", config.ZOHO_USERNAME)
                await self.page.click("button#nextbtn, #nextbtn")
                
                # Check for MFA / Verification Code screen
                await asyncio.sleep(1) # Reduced from 2s
                mfa_indicators = ["text=verification code", "text=OTP", "#otp_id", 
                                  "text=time-based", "text=authenticator app"]
                for ind in mfa_indicators:
                    try:
                        if await self.page.is_visible(ind):
                            logger.log_event("CRITICAL: MFA/OTP Prompt detected. Automation is blocked by security settings. Please disable MFA or handle login once.", level="error")
                            await self.page.screenshot(path="MFA_BLOCKER_FOUND.png")
                            return False
                    except Exception:
                        pass

                # Wait for Phase 2: Password
                try:
                    await self.page.wait_for_selector("input#password", timeout=15000)
                except Exception:
                    pass

            if await self.page.query_selector("input#password"):
                logger.log_event("Performing credential-based login (Phase 2: Password)...")
                await self.page.fill("input#password", config.ZOHO_PASSWORD)
                await self.page.click("button#nextbtn, #nextbtn")
            else:
                logger.log_event("Already logged in or direct dashboard detected.")

            # 3. Post-Login Resilience (Popups, Stay Signed In)
            await asyncio.sleep(2) # Reduced
            await self.dismiss_popups()
            
            # Handle 'Stay Signed In'
            try:
                stay_signed_in = self.page.locator("button:has-text('Yes'), button:has-text('Stay Signed In'), button.btn-primary").filter(visible=True)
                if await stay_signed_in.count() > 0:
                    logger.log_event("Clicking 'Stay Signed In'...")
                    await stay_signed_in.first.click()
                    await asyncio.sleep(1) # Reduced from 3s
            except Exception:
                pass

            # 4. Verify successful login
            logger.log_event("Verifying login completion (waiting for dashboard elements)...")
            dashboard_sel = ".zp-dashboard, .zpeople-home, .zp-attendance, .zp-left-nav, .nav_container, #zp_maintab_attendance, .zp-user-avatar, #zp_maintab_home"
            
            try:
                await self.page.wait_for_selector(dashboard_sel, timeout=60000) # Increased to 60s for "work our charm" screen
                logger.log_event("Login verified successfully.")
                return True
            except:
                # One last attempt to clear popups that might be blocking detection
                await self.dismiss_popups()
                try:
                    if await self.page.locator(dashboard_sel).count() > 0:
                        logger.log_event("Login verified successfully after late popup clearing.")
                        return True
                except Exception:
                    pass
                
                # Capture current state for debug
                try:
                    await self.page.screenshot(path="LOGIN_TIMEOUT_STATE.png")
                    logger.log_event("Login verification timed out. See LOGIN_TIMEOUT_STATE.png", level="error")
                except Exception:
                    logger.log_event("Login verification timed out and browser/page is closed.", level="error")
                return False

        except Exception as e:
            logger.log_event(f"Login process error: {str(e)}", level="error")
            return False
