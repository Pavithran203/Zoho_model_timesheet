import logging
import asyncio
import json
import os
import sys
from datetime import datetime

# Ensure logs directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Path to persistent logs
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")

# Force UTF-8 for Windows terminal compatibility
if sys.platform == "win32":
    # Set console to UTF-8 to prevent 'charmap' errors with emojis/special symbols
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ZohoLogger:
    def __init__(self):
        self.logger = logging.getLogger("ZohoModel2")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # File Handler (Full UTF-8)
            file_path = os.path.join(DATA_DIR, "automation.log")
            fh = logging.FileHandler(file_path, encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(fh)

            # Stream Handler (Safe for CMD)
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            self.logger.addHandler(sh)
        
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def log_event(self, msg, level="info"):
        # Strip emojis for stream if needed, but here we just log
        if level == "info":
            self.logger.info(msg)
        elif level == "error":
            self.logger.error(msg)
        elif level == "warning":
            self.logger.warning(msg)
            
        # Notify callbacks for real-time streaming (e.g. to Dashboard)
        for cb in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    asyncio.create_task(cb(msg, level))
                else:
                    cb(msg, level)
            except:
                pass

    def save_to_json(self, data):
        """Phase 8: Structured logging to JSON."""
        logs = []
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        data['timestamp'] = datetime.now().isoformat()
        logs.append(data)
        
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)

logger = ZohoLogger()
