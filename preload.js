const { ipcRenderer } = require('electron');

// Expose high-performance zero-allocation mouse controller API
window.mouseAPI = {
  sendMove: (x, y) => ipcRenderer.send('mouse-move', x, y),
  sendAction: (action, data) => ipcRenderer.send('mouse-action', action, data),
  getScreenSize: () => ipcRenderer.invoke('get-screen-size'),
  getCursorPos: () => ipcRenderer.invoke('get-cursor-pos'),
  toggleMiniMode: (enable) => ipcRenderer.send('toggle-mini-mode', enable),
  onGlobalToggle: (callback) => {
    ipcRenderer.on('toggle-tracking', (_event, state) => callback(state));
  }
};
