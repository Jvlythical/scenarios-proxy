import sys
import pdb
import json

STORAGE_PATH = '/tmp/entries.txt'
STORAGE_FP = open(STORAGE_PATH, 'a')

class Entry:

    def __init__(self, flow):
        self.id = flow.id
        self.started_date_time = flow.request.timestamp_start
        self.time = 0
        self.server_ip_address = flow.server_conn.ip_address[0]
        self.request = Request(flow.request)
        self.response = None

    def to_hash(self):
        return {
            'time': self.time,
            'startedDateTime': self.started_date_time,
            'request': self.request.to_hash(),
            'response': self.response.to_hash() if self.response else {},
            '_resourceType': 'xhr',
            'serverIPAddress': self.server_ip_address
        }

class Request:
    
    def __init__(self, request):
        self.method = request.method
        self.url = request.url
        self.http_version = request.http_version
        self.mime_type = ''

        self.headers = []
        self.query_params = []
        self.body_params = []
        self.cookies = []
            
        self.with_headers(request.headers)
        self.with_query_params(request.query) 
        self.with_cookies(request.cookies)
        self.with_body_params(request.multipart_form)
        self.post_data = None

        if len(self.body_params) > 0:
            self.post_data = {
                'mimeType': self.mime_type,
                'text': request.text,
                'params': self.body_params
            }

    def with_headers(self, headers):
        for header in headers.items():
            if header[0] == 'Content-Type':
                self.mime_type = header[1]

            self.headers.append({
                'name': header[0],
                'value': header[1],
            })

    def with_query_params(self, query_params):
        for query_param in query_params.items():
            self.query_params.append({
                'name': query_param[0],
                'value': query_param[1],
            })


    def with_cookies(self, cookies):
        for cookie in cookies.items():
            self.cookies.append({
                'name': cookie[0],
                'value': cookie[1]
            })

    def with_body_params(self, body_params):
        for body_param in body_params.items():
            self.body_params.append({
                'name': body_param[0],
                'value': body_param[1]
            })

    def to_hash(self):
        return {
            'method': self.method,
            'url': self.url,
            'httpVersion': self.http_version,
            'headers': self.headers,
            'queryString': self.query_params,
            'postData': self.post_data 
        }

class Response:

    def __init__(self, response):
        self.status = response.status_code
        self.status_text = response.reason
        self.http_version = response.http_version
        self.mime_type = ''

        self.headers = []
        self.cookies = []

        self.with_headers(response.headers)
        self.with_cookies(response.cookies)
        self.with_content(response.text) 

    def with_content(self, text):
        self.content = {
            'mimeType': self.mime_type,
            'size': len(text),
            'text': text
        }

    def with_headers(self, headers):
        for header in headers.items():
            if header[0] == 'Content-Type':
                self.mime_type = header[1]

            self.headers.append({
                'name': header[0],
                'value': header[1],
            })

    def with_cookies(self, cookies):
        for cookie in cookies.items():
            self.cookies.append({
                'name': cookie[0],
                'value': cookie[1][0]
            })

    def to_hash(self):
        return {
            'status': self.status,
            'statusText': self.status_text,
            'httpVersion': self.http_version,
            'headers': self.headers,
            'cookies': self.cookies,
            'content': self.content,
        }

def request(flow):
    pass

def response(flow):
    entry = Entry(flow)

    response = Response(flow.response)
    entry.response = response
    entry.time = (flow.response.timestamp_end - flow.request.timestamp_start) * 1000

    STORAGE_FP.write(json.dumps(entry.to_hash())  + "\n")

def done():
    sys.exit(1)
