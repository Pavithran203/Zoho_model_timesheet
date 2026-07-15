import asyncio
import sys
import os

# Ensure package imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser.browser_setup import BrowserManager
from browser.login_handler import LoginHandler
from browser.navigator import Navigator
from modules.extractor import DataExtractor
from modules.decision_engine import DecisionEngine
from modules.logout_executor import LogoutExecutor
from modules.worklog_updater import WorkLogUpdater
from utils.logger import logger
from datetime import datetime

async def run_zoho_automation():
    """Module 9: Controller Module."""
    browser_mgr = BrowserManager()
    execution_result = {
        "employee": "Unknown",
        "shift_end": "Unknown",
        "logout_status": "Skipped",
        "work_log_status": "Skipped",
        "error": None
    }

    try:
        # 1. Initialize Browser
        page = await browser_mgr.start()

        # 2. Login
        login_h = LoginHandler(page)
        if not await login_h.login():
            execution_result["error"] = "Login Failed"
            return execution_result

        # 3. Direct Navigation to Time Tracker
        navigator = Navigator(page)
        await navigator.to_timesheet()
        
        # 4. Work Log Update (Weekly submission)
        updater = WorkLogUpdater(page)
        work_success = await updater.submit_weekly_logs()
        execution_result["work_log_status"] = "Success" if work_success else "Partial/Failed"

        # 5. Extraction (Optional/Secondary now)
        try:
            await navigator.to_attendance()
            extractor = DataExtractor(page)
            attendance_data = await extractor.get_attendance_data()
            execution_result["employee"] = attendance_data["employee_name"]
            execution_result["shift_end"] = attendance_data["shift_end"]
            
            # 6. Decision Engine & Logout
            engine = DecisionEngine()
            if engine.should_logout(attendance_data):
                executor = LogoutExecutor(page)
                logout_success = await executor.execute_checkout()
                execution_result["logout_status"] = "Success" if logout_success else "Failed"
                await executor.sign_out_system()
        except Exception as e:
            logger.log_event(f"Attendance/Logout check skipped or failed: {e}", level="warning")

        logger.log_event("Zoho Model-2 Workflow completed successfully.")
        
        # FINAL VIEW CAPTURE: For User verification
        final_path = r"C:\Users\Pro-Admin\.gemini\antigravity\brain\71ff6f19-4c76-4731-8a4e-61236d4d5182\FINAL_RESULT.png"
        await page.screenshot(path=final_path, full_page=True)
        print(f"AUTOMATION COMPLETE. Final view saved to: {final_path}")
        
    except Exception as e:
        logger.log_event(f"Critical execution error: {str(e)}", level="error")
        execution_result["error"] = str(e)
        try:
            # Capture error state
            error_img = f"ERROR_STATE_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=error_img, full_page=True)
            logger.log_event(f"Error screenshot saved to {error_img}")
        except:
            pass
    finally:
        # Store results
        logger.save_to_json(execution_result)
        await browser_mgr.stop()
        
    return execution_result

if __name__ == "__main__":
    print("-" * 50)
    print("   ZOHO MODEL-2: PRODUCTION AUTOMATION SYSTEM   ")
    print("-" * 50)
    
    try:
        asyncio.run(run_zoho_automation())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nFailed to start automation: {e}")
