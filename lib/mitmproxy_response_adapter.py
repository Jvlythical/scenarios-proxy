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
    return self.response.raw_content