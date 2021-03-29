import re
import time
import pdb

class ResponseString:
    RESPONSE_TYPE = 2
    CLRF = "\r\n"

    def __init__(self, response, request_id):
        self.response = response
        self.lines = []
        self.latency = 0
        self.request_id = request_id

        self.response_line()
        self.headers()
        self.body()

    ###
    #
    # 1 - response type
    # 2 - request id
    # 3 - timestamp in nano seconds
    # 4 - response latency in nano seconds
    #
    def control(self):
        # @lines.unshift "#{RESPONSE_TYPE} #{@request_id} #{current_time} #{@latency}"

        current_time = self.current_time()
        self.lines.insert(0, "{} {} {} {}".format(self.RESPONSE_TYPE, self.request_id, current_time, self.latency))

    def response_line(self):
        # @lines.push "HTTP/1.1 #{@response.code}"

        self.lines.append("HTTP/1.1 {}".format(self.response.code))

    def headers(self):
        # @response.each_capitalized.each do |name, val|
        #   @lines.push ["#{to_header_case(name)}:", val].join(' ')
        # end

        headers = self.response.headers

        for name, val in headers.items():
            line = "{}: {}".format(self.to_header_case(name), val)
            self.lines.append(line)

    def body(self):
        body = self.response.body

        if not body:
            self.lines.append(self.CLRF)
        elif isinstance(body, str):
            self.lines.append("{}{}".format(self.CLRF, body))
        else:
            raise Exception("Unsupported body type")

    def with_latency(self, latency):
        # @latency = latency

        self.latency = latency

    def get(self):
        # control
        #
        # @lines.join CLRF

        self.control()
        return self.CLRF.join(self.lines)

    def to_header_case(self, header):
        # toks = header.split /_|-/
        # return header if toks.length == 1
        #
        # toks = toks.map do |tok|
        #   tok.downcase.capitalize
        # end
        # toks.join('-')

        toks = re.split('_|-', header)
        if len(toks) == 1:
            return header

        for index, tok in enumerate(toks):
            toks[index] = tok.lower().capitalize()
        return "-".join(toks)

    def current_time(self):
        # (Time.now.to_f * (10 ** 6)).round

        now = time.time()
        current_time = round(now * (pow(10, 6)))
        return current_time
