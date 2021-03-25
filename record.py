import importlib
import json
import pdb
import re
import time

import lib

from mitmproxy import http
from urllib.parse import urlparse

from lib.hashed_request_decorator import HashedRequestDecorator
from lib.joined_request import JoinedRequest
from lib.logger import Logger
from lib.mitmproxy_request_adapter import MitmproxyRequestAdapter
from lib.mitmproxy_response_adapter import MitmproxyResponseAdapter
from lib.proxy_request import ProxyRequest
from lib.settings import Settings
from lib.scenarios_api import ScenariosApi

# mitmproxy only hot reloads the main script, manually hot reload lib
importlib.reload(lib.hashed_request_decorator)
importlib.reload(lib.joined_request)
importlib.reload(lib.logger)
importlib.reload(lib.mitmproxy_request_adapter)
importlib.reload(lib.mitmproxy_response_adapter)
importlib.reload(lib.proxy_request)
importlib.reload(lib.settings)
importlib.reload(lib.scenarios_api)

LOG_ID = 'record'

MOCK_POLICY = {
    'ALL': 'all',
    'NONE': 'none',
    'FOUND': 'found',
}

RECORD_POLICY = {
    'NONE': 'none',
    'ALL': 'all',
    'NOT_FOUND': 'not_found',
}

MODE = {
    'MOCK': 'mock',
    'NONE': 'none',
    'RECORD': 'record',
}

CUSTOM_RESPONSE_CODES = {
    'NOT_FOUND': '499',
    'IGNORE_COMPONENTS': '498',
}

CUSTOM_HEADERS = {
    'MOCK_POLICY': 'X-Mock-Policy',
    'DO_PROXY': 'X-Do-Proxy',
    'PROXY_MODE': 'X-Proxy-Mode',
    'RECORD_POLICY': 'X-Record-Policy',
    'RESPONSE_LATENCY': 'X-Response-Latency',
    'SERVICE_URL': 'X-Service-Url',
}

def request(flow):
    request = flow.request

    __disable_web_cache(request)

    settings = Settings.instance()

    mode = __get_proxy_mode(request.headers, settings)
    if mode == MODE['NONE']:
        pass
    elif mode == MODE['RECORD']:
        __handle_record(request, settings)
    elif mode == MODE['MOCK']:
        __handle_mock(flow, settings)
    else:
        return __bad_request(
            flow,
            "Valid env MODE: %s, %s, Got: %s" % (MODE['RECORD'], MODE['MOCK'], mode)
        )

def response(flow):
    settings = Settings.instance()
    request = flow.request

    mode = __get_proxy_mode(request.headers, settings)
    if mode != MODE['RECORD']:
        return False

    __disable_transfer_encoding(flow.response)

    active_mode_settings = settings.active_mode_settings

    api = ScenariosApi(
      settings.api_url, settings.api_key
    )

    if active_mode_settings.get('enabled') and __path_matches(request, active_mode_settings.get('match_patterns')):
        upload_policy = __get_record_policy(request.headers, active_mode_settings)
    else:
        # If the request path does not match accepted paths, do not record
        upload_policy = RECORD_POLICY['NONE']

    if upload_policy == RECORD_POLICY['ALL']:
        __upload_request(flow, api, settings)
    elif upload_policy == RECORD_POLICY['NOT_FOUND']:
        res = __eval_request(request, api)

        if res.status_code == CUSTOM_RESPONSE_CODES['NOT_FOUND']:
            __upload_request(flow, api, settings)
    elif upload_policy == RECORD_POLICY['NONE']:
        pass
    else:
        return __bad_request(
            flow,
            "Valid env RECORD_POLICY: %s, %s, %s, Got: %s" %
            [RECORD_POLICY['ALL'], RECORD_POLICY['NOT_FOUND'], RECORD_POLICY['NONE'], upload_policy]
        )

### PRIVATE

###
#
# @param request [mitmproxy.net.http.request.Request]
# @param settings [Dict]
#
def __handle_mock(flow, settings):
    start_time = time.time()

    request = flow.request
    active_mode_settings = settings.active_mode_settings
    service_url = __get_service_url(request, active_mode_settings)

    api = ScenariosApi(
      settings.api_url, settings.api_key
    )

    if active_mode_settings.get('enabled') and __path_matches(request, active_mode_settings.get('match_patterns')):
        mock_policy = __get_mock_policy(request.headers, active_mode_settings)
    else:
        # If the request path does not match accepted paths, do not mock
        mock_policy = MOCK_POLICY['NONE']

    if mock_policy == MOCK_POLICY['NONE']:
        return __reverse_proxy(request, service_url, {})
    elif mock_policy == MOCK_POLICY['ALL']:
        res = __eval_request(request, api, active_mode_settings)

        if res.status_code == CUSTOM_RESPONSE_CODES['IGNORE_COMPONENTS']:
            res = __eval_request(request, api, actie_mode_settings, res.body)

            __simulate_latency(res[CUSTOM_HEADERS['RESPONSE_LATENCY']], start_time)
    elif mock_policy == MOCK_POLICY['FOUND']:
        res = __eval_request(request, api, active_mode_settings)

        if res.status_code == CUSTOM_RESPONSE_CODES['NOT_FOUND']:
            return __reverse_proxy(request, service_url, get_options())
        else:
            __simulate_latency(res[CUSTOM_HEADERS['RESPONSE_LATENCY']], start_time)
    else:
        return __bad_request(
            flow,
            "Valid env MOCK_POLICY: %s, %s, %s, Got: %s" %
            [MOCK_POLICY['ALL'], MOCK_POLICY['FOUND'], MOCK_POLICY['NONE'], mock_policy]
        )

    return __pass_on(flow, res)

def __handle_record(request, settings):
    active_mode_settings = settings.active_mode_settings
    service_url = __get_service_url(request, active_mode_settings)

    #
    # Try forwarding the request to the service specified by Settings.service_url
    #
    if not service_url:
        raise Exception('config service_url is not set')

    __reverse_proxy(request, service_url, {})

### API Access

def __reverse_proxy(request, service_url, options = {}):
    uri = urlparse(service_url)

    #request.scheme = uri.scheme
    #request.host = uri.hostname
    #request.port = uri.port

###
#
# Upon receiving a response, create the request in API for future use
#
# @param api [ScenariosApi]
# @param settings [Settings.mode.mock | Settings.mode.record]
# @param res [Net::HTTP::Response]
#
def __upload_request(flow, api, settings):
    active_mode_settings = settings.active_mode_settings
    service_url = __get_service_url(flow.request, active_mode_settings)
    request = MitmproxyRequestAdapter(flow.request)
    proxy_request = ProxyRequest(request, service_url)
    response = MitmproxyResponseAdapter(flow.response)

    joined_request = JoinedRequest(proxy_request).with_response(response)

    Logger.instance().info(f"Uploading {proxy_request.url()}")

    api.request_create(
        active_mode_settings.get('project_key'),
        joined_request.build(),
        {
            'importer': 'gor',
            'scenario_key': active_mode_settings.get('scenario_key'),
        }

    )

###
#
# @param api [ScenariosApi]
# @param settings [Settings.mode.mock | Settings.mode.record]
# @param ignored_components_json [String] JSON string
#
def __eval_request(request, api, settings, ignored_components_json = None):
    ignored_components = []

    if ignored_components_json:
        try:
            ignored_components = json.loads(ignored_components_json)
        except:
            pass

    query_params = __build_query_params(request, ignored_components)

    return api.request_response(
        settings.get('project_key'), query_params
    )

### Helpers

###
#
# Return response headers, body, and status code
#
def __pass_on(flow, res):
    headers = {}
    for key, value in res.headers.items():
        headers[key.capitalize()] = value

    flow.response = http.HTTPResponse.make(
        res.status_code, res.content, headers,
    )

def __bad_request(flow, message):
    flow.response = http.HTTPResponse.make(
        400,  # (optional) status code
        message,
        {'Content-Type': 'text/plain'}  # (optional) headers
    )

    return False

###
#
# @param patterns [Array<string>]
#
def __path_matches(path, patterns):
    if not patterns:
        return True

    for pattern in patterns:
        if re.match(pattern, path):
            return True

    return patterns.length == 0

###
#
# Formats request into parameters expected by scenarios api
#
# @param ignored_components [Array<Hash>]
#
# @return [Hash] query parameters to pass to scenarios api
#
def __build_query_params(request, ignored_components = []):
    request = MitmproxyRequestAdapter(request)
    hashed_request = HashedRequestDecorator(request).with_ignored_components(ignored_components)

    query_params_hash = hashed_request.query_params_hash()
    body_params_hash = hashed_request.body_params_hash()
    body_text_hash = hashed_request.body_text_hash()

    query_params = {}
    query_params['path'] = request.path
    query_params['method'] = request.method

    if len(query_params_hash) > 0:
        query_params['query_params_hash'] = query_params_hash

    if len(body_params_hash) > 0:
        query_params['body_params_hash'] = body_params_hash

    if len(body_text_hash) > 0:
        query_params['body_text_hash'] = body_text_hash

    if len(ignored_components) > 0:
        query_params['retry'] = 1

    return query_params

###
#
# Try to simulate expected response latency
#
# wait_time (seconds) = expected_latency - estimated_rtt_network_latency - api_latency
#
# expected_latency = provided value
# estimated_rtt_network_latency = 15ms
# api_latency = current_time - start_time of this request
#
def __simulate_latency(expected_latency, start_time):
    if not expected_latency.nil:
        return 0

    estimated_rtt_network_latency = 0.015 # seconds
    api_latency = (time.time() - start_time)
    expected_latency = float(expected_latency) / 1000

    wait_time = expected_latency - estimated_rtt_network_latency - api_latency

    logger.instance().debug(f"{LOG_ID}:Expected latency: {expected_latency}")
    logger.instance().debug(f"{LOG_ID}:API latency: {api_latency}")
    logger.instance().debug(f"{LOG_ID}:Wait time: {wait_time}")

    if wait_time > 0:
        time.sleep(wait_time)

    return wait_time

### Setters

def __disable_transfer_encoding(response):
    if 'Transfer-Encoding' in response.headers:
        # Without deleting this header, causes caller to stall
        del response.headers['Transfer-Encoding']

def __disable_web_cache(request):
    request.headers['CACHE-CONTROL'] = 'no-cache'

    if 'IF-NONE-MATCH' in request.headers:
        del request.headers['IF-NONE-MATCH']

### Getters

def __get_proxy_mode(headers, settings):
    if 'Access-Control-Request-Headers' in headers:
        if CUSTOM_HEADERS['DO_PROXY'].lower() in headers['Access-Control-Request-Headers']:
            return MODE['NONE']
    elif CUSTOM_HEADERS['DO_PROXY'] in headers:
        return MODE['NONE']
    elif CUSTOM_HEADERS['PROXY_MODE'] in headers:
        return headers[CUSTOM_HEADERS['PROXY_MODE']]
    else:
        return settings.active_mode

def __get_mock_policy(headers, settings):
    if CUSTOM_HEADERS['MOCK_POLICY'] in headers:
        return headers[CUSTOM_HEADERS['MOCK_POLICY']]
    else:
        return settings.get('policy')

def __get_record_policy(headers, settings):
    if CUSTOM_HEADERS['RECORD_POLICY'] in headers:
        return headers[CUSTOM_HEADERS['RECORD_POLICY']]
    else:
        return settings.get('policy')

def __get_service_url(request, settings):
    service_url = request.headers.get(CUSTOM_HEADERS['SERVICE_URL'])

    if service_url:
        return service_url
    else:
        if settings.get('service_url') and len(settings.get('service_url')) > 0:
            return settings.get('service_url')

        return f"{request.scheme}://{request.host}:{request.port}"

