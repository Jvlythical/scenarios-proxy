import pdb

from .response import  Response

class MitmproxyResponseAdapter(Response):

    def __init__(self, response):
        self.response = response

    @property
    def code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def body(self):
        content = self.response.raw_content

        if isinstance(content, bytes):
            content = content.decode('utf-8')

        return content
