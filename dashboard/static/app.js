const logList = document.getElementById('log-list');
const startBtn = document.getElementById('start-btn');
const systemStatus = document.getElementById('system-status');
const steps = {
  connect: document.getElementById('step-connect'),
  extract: document.getElementById('step-extract'),
  decide: document.getElementById('step-decide'),
  execute: document.getElementById('step-execute')
};

// State Management
let isRunning = false;

function addLog(message, type = 'info') {
  const time = new Date().toLocaleTimeString([], { hour12: false });
  const logItem = document.createElement('div');
  logItem.className = `log-item ${type}`;
  logItem.innerHTML = `
    <div class="log-time">${time}</div>
    <div class="log-content">${message}</div>
  `;
  logList.insertBefore(logItem, logList.firstChild);
  
  // Keep only last 50 logs
  if (logList.children.length > 50) {
    logList.removeChild(logList.lastChild);
  }
}

function updateStep(stepKey) {
  Object.values(steps).forEach(s => s.classList.remove('active'));
  if (steps[stepKey]) {
    steps[stepKey].classList.add('active');
  }
}

// WebSocket Connection
const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onopen = () => {
  addLog('Neural Link Established.', 'success');
  systemStatus.innerText = 'NEURAL LINK: ONLINE';
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'log') {
    addLog(data.message, data.level || 'info');
  } else if (data.type === 'status') {
    systemStatus.innerText = data.status.toUpperCase();
    if (data.step) updateStep(data.step);
  } else if (data.type === 'complete') {
    addLog('Current sequence completed.', 'success');
    updateStep(null);
    isRunning = false;
    startBtn.disabled = false;
    startBtn.innerText = 'LAUNCH BOT';
  }
};

socket.onclose = () => {
  addLog('Neural Link Severed.', 'warning');
  systemStatus.innerText = 'OFFLINE';
};

// Event Listeners
startBtn.addEventListener('click', () => {
  if (isRunning) return;
  
  isRunning = true;
  startBtn.disabled = true;
  startBtn.innerText = 'RUNNING...';
  addLog('Initiating automation sequence...', 'info');
  
  // Send start command
  socket.send(JSON.stringify({ action: 'start' }));
});
