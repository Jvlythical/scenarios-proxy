FROM python:3.7-slim

COPY init.sh /usr/local/bin/
RUN ln -s /usr/local/bin/init.sh /

COPY mitmproxy2har.py /
COPY mitmdump /

ENTRYPOINT ["init.sh", "./mitmdump"] 
