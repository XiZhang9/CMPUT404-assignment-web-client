#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Modified 2016 Han Wang, Xi Zhang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        url = str(url)     
        # delete http or https
        if url[:7]=="http://":
            url = url[7:]
        elif url[:8]=="https://":
            url = url[8:]
        
        # get host
        try:
            host_length = url.index("/")
            host = url[:host_length]
            path = url[host_length:]
        except:
            host = url
            path = "/"

        # get port number:
        try:
            port_index = host.index(":")
            port = int(host[port_index+1:])
            host = host[:port_index]
        except:
            port = 80
        return host, port, path

    def connect(self, host, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect((host, port))
  
        return client

    def get_code(self, data):
        content_list = data.split("\r\n")
        code = content_list[0].split(" ")[1]
        return int(code)

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port(url)

        send = "GET " + path + " HTTP/1.1\r\n" +\
               "Host: " + host + ":" + str(port) + "\r\n" +\
               "Accept: */*\r\n\r\n" +\
               "Connection:  Close\r\n\r\n"
        
        client = self.connect(host, port)
        
        client.sendall(send)
        receive = self.recvall(client)

        code = self.get_code(receive)
        headers = self.get_headers(receive)
        body = self.get_body(receive)


        print headers, "\n"
        print body
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        
        host, port, path = self.get_host_port(url)
        if args==None:
            content = "" #urllib.urlencode("")
        else:
            content = urllib.urlencode(args)
        
        send = "POST " + path + " HTTP/1.1\r\n" +\
               "Host: " + host + ":" + str(port) + "\r\n" +\
               "Accept: */*\r\n" +\
               "Content-Length: " + str(len(content)) + "\r\n" +\
               "Content-Type: application/x-www-form-urlencoded\r\n" +\
               "Connection:  Close\r\n\r\n" +\
               content + "\r\n\r\n"

        client = self.connect(host, port)
        
        client.sendall(send)
        receive = self.recvall(client)
        
        code = self.get_code(receive)
        headers = self.get_headers(receive)
        body = self.get_body(receive)

        print headers, "\n"
        print body

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
