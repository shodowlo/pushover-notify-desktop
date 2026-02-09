#!/usr/bin/env python3
import asyncio
import websockets
import requests
import os
import gc
import json
from pydbus import SessionBus
from gi.repository import GLib

STATE_FILE = "state.json"

if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
        json.dump({"secret": "", "device_id": ""}, f)

with open(STATE_FILE, "r") as f:
    try:
        state = json.load(f)
        SECRET = state.get("secret")
        DEVICE_ID = state.get("device_id")
    except Exception:
        SECRET = ""
        DEVICE_ID = ""
        state = {"secret": "", "device_id": ""}

if not SECRET or not DEVICE_ID:
    print("state.json is missing 'secret' or 'device_id'. Please run the setup script first.")
    exit(1)

bus = SessionBus()
notify_service = bus.get("org.freedesktop.Notifications")


def notify(title, message):
    """
    Display a notification in KDE Plasma
    """
    hints = {
        "urgency": GLib.Variant('y', 2),
        "resident": GLib.Variant('b', True),
        "category": GLib.Variant('s', 'im.received'),
        "desktop-entry": GLib.Variant('s', 'pushover-notify')
    }

    notify_service.Notify(
        "PushoverWS",
        0,
        "/home/theo/pushover-notify-desktop/server.png",
        title,
        message,
        [],
        hints,
        -1
    )
    print(f"[NOTIFICATION] {title}: {message}")


def fetch_messages():
    try:
        r = requests.get(
            "https://api.pushover.net/1/messages.json",
            params={"secret": SECRET, "device_id": DEVICE_ID},
            timeout=60
        )
        data = r.json()
        messages = data.get("messages", [])

        if not messages:
            return

        separator = "\n" + "───────────────────" + "\n"

        body = separator.join(
            (
                f"<b>{title}</b>\n{msg.get('message', '')}"
                if (title := msg.get('title'))
                else msg.get('message', '')
            )
            for msg in messages
        )
        notify("Pushover", body)

        highest_id = max(msg["id"] for msg in messages)

        # Supprimer les messages côté serveur
            f"https://api.pushover.net/1/devices/{DEVICE_ID}/update_highest_message.json",
            data={"secret": SECRET, "message": highest_id},
            timeout=10
        )

        delete_response = delete_r.json()
        if delete_response.get("status") == 1:
            print(f"Deleted {len(messages)} messages up to ID {highest_id}")
        else:
            print(f"[ERROR] Failed to delete messages: {delete_response}")

        del data, r, messages
        gc.collect()

    except Exception as e:
        print(f"[ERROR] Failed to fetch/delete messages: {e}")



async def listen():
    uri = "wss://client.pushover.net/push"
    async with websockets.connect(uri) as ws:
        login_str = f"login:{DEVICE_ID}:{SECRET}\n"
        await ws.send(login_str)
        print("Connected to Pushover WebSocket. Waiting for notifications...")

        while True:
            frame = await ws.recv()
            if isinstance(frame, bytes):
                frame = frame.decode()

            if frame == "!":
                print("New message detected.")
                fetch_messages()
            elif frame == "#":
                pass
            elif frame in ("R", "E", "A"):
                print(f"Special frame received: {frame}. Please check the connection.")
            else:
                print(f"Unknown frame received: {frame}")


if __name__ == "__main__":
    print("USER =", os.getenv("USER"))
    print("UID =", os.getuid())
    asyncio.run(listen())
