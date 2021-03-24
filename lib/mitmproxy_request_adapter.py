import pdb

from urllib.parse import urlparse

from .request import Request

class MitmproxyRequestAdapter(Request):
    def __init__(self, request):
        self.request = request

    @property
    def url(self):
        return self.request.url

    @property
    def path(self):
        uri = urlparse(self.request.path)
        return uri.path

    @property
    def base_url(self):
            return f"{self.request.scheme}://{self.request.host}:{self.request.port}"

    @property
    def method(self):
        return self.request.method

    @property
    def headers(self):
        return self.request.headers

    @property
    def body(self):
        return self.request.raw_content

    @property
    def query(self):
        return self.request.query

    @property
    def content_type(self):
        for key, value in self.headers.items():
            if key.capitalize() == 'Content-Type':
                return value
        return ''



