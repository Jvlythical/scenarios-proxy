import pdb

from lib.mitmproxy_request_adapter import MitmproxyRequestAdapter
from lib.mitmproxy_response_adapter import MitmproxyResponseAdapter
from lib.proxy_request import ProxyRequest
from lib.joined_request import JoinedRequest

def request(flow):
    pass

def response(flow):
    request = MitmproxyRequestAdapter(flow.request)
    proxy_request = ProxyRequest(request, 'test')
    response = MitmproxyResponseAdapter(flow.response)

    joined_request = JoinedRequest(proxy_request).with_response(response)

def done():
    sys.exit(1)
