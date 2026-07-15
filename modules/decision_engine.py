from utils.logger import logger
from datetime import datetime

class DecisionEngine:
    @staticmethod
    def should_logout(data):
        """Module 5: Decision Logic."""
        current_time = data["current_time"]
        shift_end = data["shift_end"]
        status = data["attendance_status"]

        logger.log_event(f"Decision logic: Time={current_time} | ShiftEnd={shift_end} | Status={status}")
        
        # Parse times for accurate comparison if possible
        try:
            # Simple string comparison works for HH:MM format
            if current_time >= shift_end and status == "Checked in":
                logger.log_event("LOGOUT REQUIRED: Shift end reached.")
                return True
            else:
                reason = "Still within shift hours" if current_time < shift_end else "Already checked out"
                logger.log_event(f"LOGOUT NOT REQUIRED: {reason}")
                return False
        except Exception as e:
            logger.log_event(f"Decision error: {str(e)}", level="error")
            return False
