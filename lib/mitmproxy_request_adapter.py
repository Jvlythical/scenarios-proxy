from .request import Request

class MitmproxyRequestAdapter(Request):
  def __init__(self, request):
    self.request = request
  
  @property
  def url(self):
    return self.request.url

  @property
  def base_url(self):
    return f"{self.request.scheme}://{self.request.host}"

  @property
  def method(self):
    return self.request.method
  
  @property
  def headers(self):
    return self.request.headers

  @property 
  def body(self):
    return self.request.raw_content


