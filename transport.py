import os
import request
import json
import time

STORAGE_PATH = '/tmp/entries.txt'
STORAGE_FP = open(STORAGE_PATH, 'r')

class Sanitizer:

    def __init__(self, obj):
        self.obj = obj 

    def sanitize(self):
        self.traverse_and_sanitize(self.obj)
        return self.obj

    def traverse_and_sanitize(self, obj):
        if isinstance(obj, list):
            for i, val in enumerate(obj):
                self.traverse_helper(obj, i, val)
        elif isinstance(obj, dict):
            for key, val in obj.items():
                self.traverse_helper(obj, key, val)
            
    def traverse_helper(self, obj, key, val):
        if self.is_traversible(val):
            self.traverse_and_sanitize(val)
        else:
            if not self.valid_value(val):
                try:
                    obj[key] = val.decode('utf-8')
                except: 
                    pass

    def valid_value(self, val):
        return isinstance(val, str) or isinstance(val, int) or isinstance(val, float)

    def is_traversible(self, val):
        return isinstance(val, dict) or isinstance(val, list)

class HAR:

    def __init__(self, entries):
        self.version = "1.2"
        self.entries = entries
        self.pages = []
        self.creator = {
            'name': 'Mitmproxy2Har',
            'version': '1.0',
        }

    def to_hash(self):
        entries = []
        for entry in self.entries:
            entries.append(entry.to_hash()) 

        return {
            'log': {
                'version': self.version,
                'entries': self.entries,
                'pages': self.pages,
                'entries': entries
            }
        }

    def to_sanitized_hash(self):
        h = self.to_hash()
        s = Sanitizer(h)
        return s.sanitize()

class ScenarioProxy:

    def __init__(self):
        self.service_url = 'http://localhost:3000'
        self.requests_path = 'requests'

    def requests_create(har_dict):
        path = "%s/%s" % [self.service_url, self.requests_path]
        headers = {
            'HTTP_X_API_KEY': os.environ['SCENARIO_API_KEY'],
        }
        body = {
            'project_id': os.environ['SCENARIO_PROJECT_ID'], 
            'requests': har_dict,
        }

        requests.post(path, data = body, headers = headers)

if __name__ == '__main__':
    proxy = ScenarioProxy()

    while True:
        entries = []        

        entries_json_list = fp.read().split("\n")
        if len(entries_json_list) > 0:
            for entries_json in entries_json_list:
                try:
                    entries.append(json.loads(entries_json))
                except:
                    continue 

            har = HAR(entries)
            har_dict = har.to_sanitized_hash()

            proxy.requests_create(har_dict)

        time.sleep(5)
