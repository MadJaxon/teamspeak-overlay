class TSApiConfig:
    def __init__(self, config=None):
        self.config = {
            'api': {
                'host': 'localhost',
                'port': 5899,
                'key': '',
                'tsEventDebug': False
            },
            'app': {
                'name': "TS Overlay",
                'identifier': "ts5-overlayy",
                'version': "1.0.0",
                'description': "An TeamSpeak 5 compatible barebones overlay",
            }
        }
        if config:
            self.merge_config(config)

    def merge_config(self, new_config):
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value

    def get(self, key=None):
        if key is None:
            return self.config
        return self.config.get(key)

    def set(self, config):
        self.merge_config(config)