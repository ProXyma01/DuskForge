# DuskForge

DuskForge is a Python-based tool designed to simplify downloading and installing addons and patches for *World of Warcraft* (version 3.3.5a). With an intuitive GUI, it allows users to manage WoW addons, patches, and server settings effortlessly.

![DuskForge Screenshot](https://github.com/ProXyma01/DuskForge/assets/50544553/ea854d74-0092-405c-86e7-c549c44235d4)

## Features
- **Addon Management**: Download and install WoW addons with tooltips showing previews on hover.
- **Patch Support**: Install and manage patches (tested on Warmane’s legacy client).
- **Dynamic Patch Checking**: View, pause, or delete downloaded patches via the "Check Downloads" window.
- **Server Switching**: Toggle between Warmane and Warsong servers with realmlist updates.
- **Game Launcher**: Start WoW directly from the app.
- **Standalone**: Distributed as a single `.exe` file for Windows.

## Installation

1. **Download**: Grab the latest `Duskforge.exe` from the [Releases](https://github.com/ProXyma01/DuskForge/releases) page.
2. **Windows Security Note**: Windows Defender may flag the `.exe` as a False Positive. You might need to disable Defender or add an exception to run it.
3. **Linux Users**: Run the `.exe` with Wine:

   ```bash
   wine Duskforge.exe

# NOTE
1) In case the downloaded patches cause the game to crash or the textures to change, e.g.:

![alt text](https://i.imgur.com/sq3qr.jpeg)

![alt text](https://i.imgur.com/DlmD50Z.jpeg)

You can use the {Pause} button, which will temporarily comment/pause the specific patch and it will not load again the next time you start the game.
To enable it, use the same button again.
