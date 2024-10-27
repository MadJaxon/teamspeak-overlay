from collections import defaultdict
from wrapper.TSApiConfig import TSApiConfig
from wrapper.TSApiConnection import TSApiConnection


class TSApiWrapper:
    def __init__(self, config):
        self.config = TSApiConfig(config)
        self.connection = None
        self.events = defaultdict(list)

    def connect(self) -> bool:
        if self.connection and (self.connection.is_open or self.connection.is_connecting):
            return False
        self.connection = TSApiConnection(self.config)

        self.connection.on('error', lambda params: self.emit('apiError', params))
        self.connection.on('close', lambda params: self.emit('apiConnectionClosed', params))
        self.connection.on('open', lambda params: self.emit('apiConnectionOpen', params))
        self.connection.on('message', self.message_handler)
        self.connection.on('ready', lambda message: self.emit('apiReady', message['payload']))
        return True

    def run_forever(self):
        self.connection.run_forever()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def send(self, data):
        if self.connection:
            self.connection.send(data)

    def message_handler(self, message):
        if self.config.get('api')['tsEventDebug']:
            print(f"Event received: {message['type']}")
            print(message)

        self.emit(message['type'], message['payload'])

    def on(self, event, callback):
        self.events[event].append(callback)

    def off(self, event, callback):
        if event in self.events:
            self.events[event] = [cb for cb in self.events[event] if cb != callback]

    def emit(self, event, *args):
        sent = False
        for callback in self.events[event]:
            callback(*args)
            sent = True
        if not sent:
            print("missing event handler")
            print(event)
            # print(args)