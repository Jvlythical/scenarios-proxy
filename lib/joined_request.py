import time

from .request_string import RequestString
from .response_string import ResponseString

class JoinedRequest:
  REQUEST_DELIMITTER = '🐵🙈🙉'

  ###
  #
  # @params proxy_request [ProxyRequest]
  #
  def __init__(self, proxy_request):
    self.timestamp = time.time()
    self.proxy_request = proxy_request

    self.request_string = RequestString(proxy_request)

  def with_response(self, response):
    now = time.time()

    self.response_string = ResponseString(response, self.request_string.request_id)

    # milliseconds
    latency = round((now - self.timestamp) * (10 ** 6))
    self.response_string.with_latency(latency)

    return self

  def build(self):
    if not self.response_string:
      raise Exception('Missing response')

    request_string = self.request_string.get()
    response_string = self.response_string.get()

    return self.REQUEST_DELIMITTER.join([request_string, response_string])
