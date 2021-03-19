# Modeled after Net::HTTP::Response

class Response:
  def __init__(self):
    self.code = 0
    self.headers = {}
    self.body = ""

  def with_code(self, code):
    self.code = code
    return self

  def with_headers(self, headers):
    self.headers = headers
    return self

  def with_body(self, body):
    self.body = body
    return self
