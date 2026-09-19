const { app, BrowserWindow, screen, ipcMain, globalShortcut, session } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, execSync } = require('child_process');

// Auto-grant camera permissions without blocking popups
app.commandLine.appendSwitch('use-fake-ui-for-media-stream');
app.commandLine.appendSwitch('enable-features', 'MediaStreamTrack');
// Prevent Chromium from throttling, freezing, or sleeping when backgrounded, occluded, or minimized
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('disable-features', 'CalculateNativeWinOcclusion');

let win = null;
let mouseProcess = null;
let isMiniMode = false;
let normalBounds = { width: 1280, height: 860, x: undefined, y: undefined };
let trackingEnabled = true;

// Ensure mouse_service.exe is compiled
function ensureMouseService() {
  const exePath = path.join(__dirname, 'mouse_service.exe');
  const csPath = path.join(__dirname, 'mouse_service.cs');
  if (!fs.existsSync(exePath) && fs.existsSync(csPath)) {
    try {
      const cscPath = 'C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe';
      execSync(`"${cscPath}" /nologo /optimize+ /out:"${exePath}" "${csPath}"`);
      console.log('Compiled mouse_service.exe successfully.');
    } catch (err) {
      console.error('Failed to compile mouse_service.cs:', err);
    }
  }

  if (fs.existsSync(exePath)) {
    try {
      mouseProcess = spawn(exePath, [], {
        stdio: ['pipe', 'pipe', 'inherit'],
        windowsHide: true
      });
      mouseProcess.on('error', (err) => {
        console.error('Mouse service error:', err);
      });
      mouseProcess.on('exit', (code) => {
        console.log('Mouse service exited with code', code);
      });
    } catch (e) {
      console.error('Failed to spawn mouse service:', e);
    }
  } else {
    console.warn('mouse_service.exe not found. OS mouse movements will be simulated.');
  }
}

function sendMouseCommand(cmd) {
  if (mouseProcess && mouseProcess.stdin && !mouseProcess.killed) {
    try {
      mouseProcess.stdin.write(cmd + '\r\n');
    } catch (e) {}
  }
}

function createWindow() {
  win = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 320,
    minHeight: 220,
    title: 'CyberMouse Pro - AI Hand Virtual Mouse',
    backgroundColor: '#070a13',
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      backgroundThrottling: false, // Disables background throttling when window is minimized or behind other windows
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: false,
      webSecurity: false // Allows loading MediaPipe WASM assets smoothly
    }
  });

  // Automatically approve media/camera permissions
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(true);
  });

  session.defaultSession.setPermissionCheckHandler(() => true);

  // Press F12 to toggle DevTools if needed
  win.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F12' && input.type === 'keyDown') {
      win.webContents.toggleDevTools();
    }
  });

  win.loadFile(path.join(__dirname, 'hand-tracer', 'index.html'));

  win.once('ready-to-show', () => {
    win.show();
  });

  win.on('resize', () => {
    if (!isMiniMode) {
      normalBounds = win.getBounds();
    }
  });
}

// IPC Handlers
ipcMain.handle('get-screen-size', () => {
  const primaryDisplay = screen.getPrimaryDisplay();
  return {
    width: primaryDisplay.bounds.width,
    height: primaryDisplay.bounds.height,
    scaleFactor: primaryDisplay.scaleFactor
  };
});

ipcMain.handle('get-cursor-pos', () => {
  try {
    const pt = screen.getCursorScreenPoint();
    return { x: pt.x, y: pt.y };
  } catch (e) {
    return { x: 960, y: 540 };
  }
});

ipcMain.on('mouse-move', (event, x, y) => {
  sendMouseCommand(`M ${Math.round(x)} ${Math.round(y)}`);
});

ipcMain.on('mouse-action', (event, action, data) => {
  if (action === 'LD' || action === 'LU' || action === 'CLICK' || action === 'RD' || action === 'RU' || action === 'RC') {
    sendMouseCommand(action);
  } else if (action === 'W') {
    sendMouseCommand(`W ${Math.round(data || 0)}`);
  }
});

ipcMain.on('toggle-mini-mode', (event, enable) => {
  if (!win) return;
  const primary = screen.getPrimaryDisplay();
  const screenBounds = primary.workArea;

  if (enable) {
    if (!isMiniMode) {
      normalBounds = win.getBounds();
    }
    isMiniMode = true;
    const miniW = 340;
    const miniH = 240;
    // Dock to bottom-right corner with 20px margin
    const posX = screenBounds.x + screenBounds.width - miniW - 20;
    const posY = screenBounds.y + screenBounds.height - miniH - 20;
    win.setBounds({ x: posX, y: posY, width: miniW, height: miniH }, true);
    win.setAlwaysOnTop(true, 'screen-saver');
  } else {
    isMiniMode = false;
    win.setAlwaysOnTop(false);
    win.setBounds(normalBounds, true);
  }
});

app.whenReady().then(() => {
  ensureMouseService();
  createWindow();

  // Register global hotkey to pause/resume virtual mouse tracking anywhere
  try {
    globalShortcut.register('F8', () => {
      trackingEnabled = !trackingEnabled;
      if (win && !win.isDestroyed()) {
        win.webContents.send('toggle-tracking', trackingEnabled);
      }
    });
  } catch (e) {}

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  if (mouseProcess) {
    sendMouseCommand('Q');
    try {
      mouseProcess.kill();
    } catch (e) {}
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
