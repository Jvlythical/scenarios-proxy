import os
import yaml
import pdb

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from .logger import Logger

class Settings:
    LOG_ID = 'lib.settings'

    _instance = None

    def __init__(self):
        if Settings._instance:
            raise RuntimeError('Call instance() instead')
        else:
            cwd = os.path.dirname(os.path.realpath(__file__))
            self.config_file_path = os.path.join(cwd, '..', 'config', 'settings.yml')

            self.__load_config()
            self.__observe_config()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    @property
    def agent_url(self):
        return self.config.get('agent_url')

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

    def reload_config(self, event):
        Logger.instance().info(f"{self.LOG_ID}.reload_config")
        self.__load_config()

    def __load_config(self):
        with open(self.config_file_path, 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                pass

    def __observe_config(self):
        patterns = "*"
        ignore_patterns = ""
        ignore_directories = False
        case_sensitive = True
        event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

        event_handler.on_modified = self.reload_config

        observer = Observer()
        observer.schedule(event_handler, self.config_file_path)
        observer.start()
