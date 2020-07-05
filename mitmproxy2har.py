import sys
import pdb

entry_map = {}
entries = []

class Entry:

    def __init__(self, flow):
        self.id = flow.id
        self.started_date_time = flow.request.timestamp_start
        self.request = Request(flow.request)
        self.response = None

    def to_hash(self):
        return {
            'startedDateTime': self.started_date_time,
            'request': self.request.to_hash(),
            'response': self.response.to_hash() if self.response else {}
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
                'name': query_params[0],
                'value': query_params[1],
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

        self.content = {
            #'mimeType': self.headers['Content-Type'],
            'size': len(response.text),
            'text': response.text
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
                'value': cookie[1]
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
    print("Request %s" % flow.id)

    entry = Entry(flow)
    entries.append(entry)
    entry_map[flow.id] = entry

def response(flow):
    print("Response %s" % flow.id)

    response = Response(flow.response)

    if flow.id in entry_map:
        entry = entry_map[flow.id]
        entry.response = response
        pdb.set_trace()

def done():
    sys.exit(1)  # we did not see the request
