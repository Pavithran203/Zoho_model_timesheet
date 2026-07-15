import asyncio
import json
import os
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import uvicorn
from contextlib import asynccontextmanager

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing automation logic (if possible)
from main import run_zoho_automation
from utils.logger import logger as zoho_logger

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "start":
                asyncio.create_task(execute_sequence())
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def log_callback(message, level):
    print(f"WEB_BROADCAST: [{level.upper()}] {message}")
    await manager.broadcast({"type": "log", "message": message, "level": level})

zoho_logger.register_callback(log_callback)

async def execute_sequence():
    """Trigger the real automation sequence and stream logs."""
    print("TASK_START: execute_sequence initiated")
    print("DEBUG: broadcasting running status...")
    await manager.broadcast({"type": "status", "status": "running", "step": "connect"})
    print("DEBUG: broadcast done. calling run_zoho_automation...")
    
    try:
        # Run the real automation from main.py
        result = await run_zoho_automation()
        
        if result.get("error"):
            await manager.broadcast({"type": "log", "message": f"Automation Failed: {result['error']}", "level": "error"})
        else:
            await manager.broadcast({"type": "log", "message": "Automation Sequence Finished Successfully.", "level": "success"})
        
        await manager.broadcast({"type": "complete", "result": result})
        
    except Exception as e:
        await manager.broadcast({"type": "log", "message": f"Server Error: {str(e)}", "level": "error"})
        await manager.broadcast({"type": "complete"})

async def monitor_emails():
    """Background task to watch for 'do it' commands."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trigger_file = os.path.join(root_dir, "mock_email.txt")
    print(f"DEBUG: Monitoring trigger file at {trigger_file}")
    
    while True:
        if os.path.exists(trigger_file):
            print(f"DEBUG: Trigger file detected at {datetime.now()}")
            try:
                with open(trigger_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower().strip()
                    print(f"DEBUG: File content: '{content}'")
                    if "do it" in content or "complete" in content:
                        print("EMAIL_TRIGGER: 'do it' detected!")
                        await manager.broadcast({"type": "log", "message": "Trigger received via Email Sync: 'DO IT'", "level": "success"})
                        await execute_sequence()
                os.remove(trigger_file)
            except Exception as e:
                print(f"DEBUG: Error reading trigger file: {e}")
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the email monitor
    asyncio.create_task(monitor_emails())
    yield
    # Shutdown logic (if any) could go here

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
