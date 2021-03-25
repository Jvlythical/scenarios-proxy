import os
import yaml
import pdb

class Settings:
    _instance = None

    def __init__(self):
        if Settings._instance:
            raise RuntimeError('Call instance() instead')
        else:
            cwd = os.path.dirname(os.path.realpath(__file__))
            self.config_file_path = os.path.join(cwd, '..', 'config', 'settings.yml')

            with open(self.config_file_path, 'r') as stream:
                try:
                    self.config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    @property
    def api_url(self):
        return self.config.get('api_url')

    @property
    def api_key(self):
        return self.config.get('api_key')

    @property
    def mode(self):
        return self.config.get('mode')

    @property
    def active_mode(self):
        mode = self.mode

        if not mode:
            return None
        else:
            return mode.get('active')

    @property
    def active_mode_settings(self):
        mode = self.mode

        if not mode:
            return None

        active_mode = self.active_mode

        if not active_mode:
            return None

        return mode.get(active_mode)
