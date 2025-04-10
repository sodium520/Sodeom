const { app, BrowserWindow, Menu } = require('electron');

function createWindow() {
  // Create the browser window.
  let win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,      // Disable Node integration for security
      contextIsolation: true,      // Enable context isolation for security
      webviewTag: true             // Enable the <webview> tag
    }
  });

  // Load the index.html of the app.
  win.loadFile('index.html');
  
  // Uncomment to open DevTools.
  // win.webContents.openDevTools();
}

// When Electron has finished initialization, remove the default menu and create the window.
app.whenReady().then(() => {
  Menu.setApplicationMenu(null); // Remove the default menu
  createWindow();
});

app.on('window-all-closed', () => {
  // On macOS, apps often stay active until the user quits explicitly.
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, recreate a window when the dock icon is clicked.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});