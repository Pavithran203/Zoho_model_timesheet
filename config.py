import os
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# Zoho Credentials
ZOHO_USERNAME = os.getenv("ZOHO_USERNAME", "your_email@zoho.com")
ZOHO_PASSWORD = os.getenv("ZOHO_PASSWORD", "your_password")

# Portal Settings
PORTAL_URL = "https://people.zoho.in/group10/zp"

# Wait times
TIMEOUT = 30000  # 30 seconds
HEADLESS = False  # Set to True for production background runs

# File Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
OS_LOG_FILE = os.path.join(DATA_DIR, "zoho_automation.log")
