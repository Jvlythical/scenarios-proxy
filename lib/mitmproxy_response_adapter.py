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
        content = self.response.content

        if not content:
            return ''

        try:
            if isinstance(content, bytes):
                return content.decode('utf-8')
        except:
            return ''.join(map(chr, content))

        return content
