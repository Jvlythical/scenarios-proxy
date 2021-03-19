# Rails request object
# https://guides.rubyonrails.org/action_controller_overview.html#the-request-object
class Request:
    def __init__(self):
        self.method = ""
        self.url = ""
        self.base_url = ""
        self.headers = {}
        self.body = ""

    def with_method(self, method):
        self.method = method
        return self

    def with_url(self, url):
        self.url = url
        return self

    def with_base_url(self, base_url):
        self.base_url = base_url
        return self

    def with_headers(self, headers):
        self.headers = headers
        return self

    def with_body(self, body):
        self.body = body
        return self
