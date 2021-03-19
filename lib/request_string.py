import hashlib
import time
import pdb

class RequestString:
    request_id = 0
    REQUEST_TYPE = 1
    CLRF = "\r\n"

    def __init__(self, proxy_request):
        self.request = proxy_request.request
        self.proxy_request = proxy_request


        self.lines = []

        self.request_line()
        self.headers()
        self.body()

        self.request_id = self.generate_request_id()
        self.control()

    def get(self):
        # @lines.join CLRF

        return self.CLRF.join(self.lines)

    def control(self):
        # @lines.unshift "#{REQUEST_TYPE} #{@request_id} #{current_time}"

        current_time = self.current_time()
        self.lines.insert(0, "{} {} {}".format(self.REQUEST_TYPE, self.request_id, current_time))


    def request_line(self):
        # import pdb
        # pdb.set_trace()
        self.lines.append("{} {} HTTP/1.1".format(self.request.method, self.proxy_request.url()))

    def headers(self):
        # _headers = self.request.headers.env.reject { |key| key.to_s.include?('.') }
        # _headers.each do |name, val|
        #     @lines.push ["#{to_header_case(name)}:", val].join(' ')
        # end

        # headers_env = self.request.headers.env
        # _headers = [item for item in headers_env if not "." in item]

        _headers = self.request.headers

        for name, val in _headers.items():
            line = ' '.join(["{}:".format(self.to_header_case(name)), val])
            self.lines.append(line)

    def body(self):
        self.lines.append("{}{}".format(self.CLRF, self.request.body))

    def to_header_case(self, header):
        # toks = header.split('_')
        # toks = toks.map do |tok|
        #     tok.downcase.capitalize
        # end
        # toks.join('-')

        toks = header.split('_')
        for index, tok in enumerate(toks):
            toks[index] = tok.lower().capitalize()
        return "-".join(toks)

    def generate_request_id(self):
        joined_lines = self.CLRF.join(self.lines)
        return hashlib.md5(joined_lines.encode('utf-8')).hexdigest()

    def current_time(self):
        # (Time.now.to_f * (10 ** 9)).round

        now = time.time()
        current_time = round(now * (pow(10, 9)))
        return current_time
