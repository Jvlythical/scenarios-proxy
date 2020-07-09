import sys
import pdb
import json

entries = []

class Sanitizer:

    def __init__(self, obj):
        self.obj = obj 

    def sanitize(self):
        self.traverse_and_sanitize(self.obj)
        return h

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
        return isinstance(value, dict) or isinstance(value, list)

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

    def to_hash(self):
        h = self.to_hash()
        s = Sanitizer(h)
        return s.sanitize()
        
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
        self.headers = []
        self.query_params = []
        self.body_params = []
        self.cookies = []
            
        self.with_headers(request.headers)
        self.with_query_params(request.query) 
        self.with_cookies(request.cookies)
        self.with_body_params(request.multipart_form)

    def with_headers(self, headers):
        for header in headers.items():
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
            'postData': self.body_params
        }

class Response:

    def __init__(self, response):
        self.status = response.status_code
        self.status_text = response.reason
        self.http_version = response.http_version
        self.headers = []
        self.cookies = []

        self.with_headers(response.headers)
        self.with_cookies(response.cookies)
        self.with_content(response.text) 

    def with_content(self, text):
        try:
            text = text.decode()
        except:
            pass

        self.content = {
            #'mimeType': self.headers['Content-Type'],
            'size': len(text),
            'text': text
        }

    def with_headers(self, headers):
        for header in headers.items():
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

    entries.append(entry)

def done():
    har = HAR(entries)
    fp = open('/tmp/scenario.har', 'w')
    fp.write(json.dumps(har.to_hash(), indent=2))
    sys.exit(1)
