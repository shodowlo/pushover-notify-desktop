# Pushover Notify Desktop

A Python 3 application to receive real-time Pushover notifications on your desktop.  

Supports Linux (tested on KDE), with future plans for Windows support.

## Features

- Real-time notifications via Pushover WebSocket.   
- Lightweight and simple Python 3 implementation.

## Requirements

- Python 3
- Install dependencies:

```bash
pip install requests websockets pydbus PyGObject
```
Linux only for now. Windows support will be added in the future.

## Setup
Run the setup script to register a Pushover device:

```bash
python3 setup_device.py
```

- Enter your Pushover email and password
- Choose a device name (default: pushover-notify-desktop)
- It creates state.json containing your secret and device_id

## Usage
Run the main notifier:
```bash
python3 pushover_ws_notifier.py
```

- Connects to Pushover WebSocket
- Fetches new messages
- Notify and delete from pushover
