#!/usr/bin/env python3
import requests
import json
import os

STATE_FILE = "state.json"

def save_state(secret, device_id):
    state = {"secret": secret, "device_id": device_id}
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    print("state.json created with secret and device_id.")

def login():
    while True:
        email = input("Pushover Email: ").strip()
        password = input("Pushover Password: ").strip()
        try:
            r = requests.post(
                "https://api.pushover.net/1/users/login.json",
                files={"email": (None, email), "password": (None, password)},
                timeout=10
            )
            data = r.json()
            if r.status_code == 200 and "secret" in data:
                print("Login successful.")
                return data["secret"]
            else:
                print(f"Login error: {data}")
        except Exception as e:
            print(f"Exception during login: {e}")
        print("Please try again.\n")

def create_device(secret):
    default_name = "pushover-python-notify"
    name = input(f"Device name (default: {default_name}): ").strip() or default_name
    os_name = "O"  # Linux/OS arbitrary, can remain "O"
    try:
        r = requests.post(
            "https://api.pushover.net/1/devices.json",
            files={
                "secret": (None, secret),
                "name": (None, name),
                "os": (None, os_name)
            },
            timeout=10
        )
        data = r.json()
        if r.status_code == 200 and "id" in data:
            print(f"Device created: {data['id']}")
            return data["id"]
        else:
            print(f"Device creation error: {data}")
            return None
    except Exception as e:
        print(f"Exception during device creation: {e}")
        return None

def main():
    print("=== Pushover Device Setup ===")
    secret = login()
    device_id = None
    while not device_id:
        device_id = create_device(secret)
    save_state(secret, device_id)
    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
