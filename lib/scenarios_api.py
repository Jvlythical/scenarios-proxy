import base64
import json
import requests
import urllib
import pdb

from jwt import JWT

from .logger import Logger

class ScenariosApi:
    LOG_ID = 'lib.scenarios_api'
    REQUESTS_ENDPOINT = '/requests'

    def __init__(self, service_url, api_key):
        self.service_url = service_url
        self.api_key = api_key

    @staticmethod
    def decode_project_key(key):
        # TODO: add specific error catching
        try:
            key = base64.b64decode(key)
        except:
            return {}

        # TODO: add specific error catching
        try:
            return json.loads(key)
        except:
            return {}

    @staticmethod
    def decode_scenario_key(jwt):
        try:
            key = base64.b64decode(key)
        except:
            return {}

        try:
            return json.loads(key)
        except:
            return {}

    @property
    def default_headers(self):
        return {
            'X_API_KEY': self.api_key,
        }

    def request_create(self, project_key, raw_requests, params):
        url = f"{self.service_url}{self.REQUESTS_ENDPOINT}"

        self.__parse_scenario_key(params)

        body = {
            'project_id': self.decode_project_key(project_key)['id'],
            'requests': raw_requests,
            **params,
        }

        return requests.post(url, headers=self.default_headers, data=body)

    def request_response(self, project_key, query_params):
        url = f"{self.service_url}{self.REQUESTS_ENDPOINT}/response"

        self.__parse_scenario_key(query_params)

        params = {
            'project_id': self.decode_project_key(project_key)['id'],
            **query_params,
        }

        Logger.instance().debug(f"{self.LOG_ID}.request_response:{url}?{urllib.parse.urlencode(params)}")

        return requests.get(url, headers=self.default_headers, params=params)

    def __parse_scenario_key(self, params):
        if 'scenario_key' in params:
            if len(params['scenario_key']) > 0:
                scenario_id = self.decode_scenario_key(params['scenario_key'])['id']
                params['scenario_id'] = scenario_id

            del params['scenario_key']
