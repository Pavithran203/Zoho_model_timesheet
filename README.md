# Zoho People Automation System (Model-2)

An intelligent, module-driven Python automation agent powered by **Playwright** that automates employee timesheet logging and attendance management on the Zoho People platform.

This repository features a robust, automated workflow designed to handle weekly work log submissions, check daily attendance records, and automatically execute secure sign-outs based on shift completion—ensuring zero manual errors and saving time.

---

## 🌟 Key Features

* **Weekly Work Log Automator (`WorkLogUpdater`)**: Automatically submits daily timesheet entries for the current week (Monday to Friday). It performs live checking to skip already logged dates, preventing duplicate entries.
* **Natural Log Variation**: Randomizes work log minutes (e.g., `08:14`, `08:29`) and rotates daily task descriptions to mimic human-like entry behavior.
* **Attendance Parser (`DataExtractor`)**: Dynamically navigates to the attendance portal and extracts critical shift information, including employee names and shift end-times.
* **Automated Decision Engine (`DecisionEngine`)**: Uses structured rules to evaluate attendance metadata and decide if the employee should log out or stay signed in.
* **Graceful Checkout & Logout**: Executes safe portal checkouts, performs system-level sign-outs, and closes browser instances cleanly.
* **Comprehensive Logging**: Detailed execution audits written in both JSON (`logs.json`) and standard log files (`zoho_automation.log`).
* **Visual Validation**: Automatically captures full-page browser screenshots on success or error for post-run verification.

---

## 🏗️ Architecture & Modules

The system is decoupled into logical modules for clean separation of concerns:

```
├── browser/
│   ├── browser_setup.py  # Headless/headed Playwright browser manager
│   ├── login_handler.py  # Zoho credentials login flows and MFA handler
│   └── navigator.py      # Direct portal route navigation (Timesheet, Attendance)
├── modules/
│   ├── extractor.py      # Scrapes attendance shift timings and employee name
│   ├── decision_engine.py# Business rules engine for checkouts
│   ├── worklog_updater.py# Scrapes existing logs and submits daily hours
│   └── logout_executor.py# Executes check-out and sign-out actions
├── utils/
│   └── logger.py         # Thread-safe event and JSON data logging utilities
├── config.py             # Configuration parameters and environment variables
├── requirements.txt      # Python dependencies
├── .env.example          # Sample environment template
└── main.py               # Application orchestrator / Entry point
```

---

## 🚀 Getting Started

### 📋 Prerequisites

* **Python 3.8+**
* **Git**
* **Zoho People Account** with active login credentials

### 🔧 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/zoho-people-automation.git
   cd zoho-people-automation
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers:**
   ```bash
   playwright install
   ```

5. **Configure Environment Variables:**
   * Duplicate `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   * Open the `.env` file and fill in your credentials:
     ```env
     ZOHO_USERNAME=your_email@zoho.com
     ZOHO_PASSWORD=your_secure_password
     ```
     > [!IMPORTANT]
     > Never commit your `.env` file containing real credentials to GitHub. The project's `.gitignore` is pre-configured to keep it safe.

---

## 💻 Usage

To run the automation script, execute the following command:

```bash
python main.py
```

### Script Execution Flow:
1. Launches the Playwright browser.
2. Authenticates onto the Zoho portal.
3. Accesses the **Time Logs** list and scrapes already logged dates.
4. Fills and saves missing logs for the week (Monday through current day).
5. Scrapes attendance metadata to check shift duration.
6. Evaluates shift status and, if eligible, performs automatic **Checkout** and **Sign Out**.
7. Captures a final confirmation screenshot and saves execution logs.

---

## 🛠️ Technologies Used

* **Language:** Python
* **Automation:** Playwright for Python
* **Environment Management:** python-dotenv
* **Logging:** Built-in Python Logging & Custom JSON Logger
