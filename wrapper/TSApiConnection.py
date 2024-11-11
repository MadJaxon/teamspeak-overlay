import os
from collections import defaultdict
import json
from datetime import datetime, timedelta

import websocket

class TSApiConnection:
    def __init__(self, config):
        self.config = config
        self.socket_url = f"ws://{self.config.get('api')['host']}:{self.config.get('api')['port']}/"
        self.ws = websocket.WebSocketApp(
            self.socket_url,
            None,
            self.on_open,
            None,
            self.on_message,
            self.on_error,
            self.on_close
        )

        self.events = defaultdict(list)
        self.is_connecting = True
        self.is_open = False
        self.is_authenticated = False
        self.auth_request_sent = False

    def run_forever(self):
        self.ws.run_forever()

    def on_open(self, ws):
        self.is_connecting = False
        self.is_open = True
        self.auth()
        self.emit('open', ws)

    def on_reconnect(self, ws):
        print("on_reconnect")
        self.is_connecting = True
        self.is_open = False
        self.emit('reconnect', ws)

    def on_error(self, ws, error):
        data = {
            'socketEvent': error,
            'exception': Exception("Error connecting to TeamSpeak remote apps API.")
        }
        self.emit('error', data)

    def on_close(self, ws, close_status_code, close_msg):
        if self.auth_request_sent and not self.is_authenticated:
            data = {
                'socketEvent': (close_status_code, close_msg),
                'exception': Exception("Access to TS API denied.")
            }
            self.emit('error', data)

        self.is_open = False
        self.is_connecting = False
        self.is_authenticated = False
        self.emit('close', (close_status_code, close_msg))

    def on_message(self, ws, message):
        message = json.loads(message)
        if message.get('type') == "auth":
            self.handle_auth_response(message)
        else:
            self.emit('message', message)

    def auth(self):
        # Check if the file exists
        if os.path.isfile("api_key.txt"):
            now = datetime.now()

            # Get the file modification time in seconds since epoch
            file_mod_time = os.path.getmtime("api_key.txt")

            # Convert modification time to datetime object
            file_mod_datetime = datetime.fromtimestamp(file_mod_time)

            # Calculate the time difference
            time_difference = now - file_mod_datetime

            # Check if the file is older than 1 week
            isFromToday = time_difference <= timedelta(7)
            if isFromToday:
                with open("api_key.txt", "r") as reader:
                    key = reader.readline()
                    self.config.set({'api': {'key': key}})
                    # Update the file's modification time
                    current_time = datetime.now()
                    os.utime("api_key.txt", (current_time.timestamp(), current_time.timestamp()))

        payload = {
            "type": "auth",
            "payload": {
                "identifier": self.config.get('app')['identifier'],
                "version": self.config.get('app')['version'],
                "name": self.config.get('app')['name'],
                "description": self.config.get('app')['description'],
                "content": {
                    "apiKey": self.config.get('api')['key']
                }
            }
        }
        print("Waiting on authorization from Teamspeak")
        self.ws.send(json.dumps(payload))
        self.auth_request_sent = True

    def handle_auth_response(self, message):
        self.config.set({'api': {'key': message['payload']['apiKey']}})
        self.is_authenticated = True
        self.emit('ready', message)
        with open('api_key.txt', 'w') as writer:
            writer.write(message['payload']['apiKey'])

    def send(self, data):
        if not self.is_open:
            raise Exception("Can't send data to API. Connection not open.")
        if not self.is_authenticated:
            raise Exception("Can't send data to API. Not authenticated.")
        self.ws.send(json.dumps(data))

    def close(self):
        if self.is_open:
            self.is_open = False
            self.ws.close()
        elif self.is_connecting:
            raise Exception("Can not close connection that is still connecting")

    def on(self, event, callback):
        self.events[event].append(callback)

    def off(self, event, callback):
        if event in self.events:
            self.events[event] = [cb for cb in self.events[event] if cb != callback]

    def emit(self, event, *args):
        for callback in self.events[event]:
            callback(*args)