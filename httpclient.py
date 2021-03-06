#!/usr/bin/env python
# coding: utf-8

# Copyright 2016 Shawn Anderson

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

def help():
	print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
	def __init__(self, code=200, body=""):
		self.code = code
		self.body = body


class HTTPClient(object):
	
	
	def rmList(self, l):
		if isinstance(l, list):
			return l[0]
		else:
			return l

	def get_host_port(self,url):
		url = url.split("://")
		if(len(url) >= 2):
			url = "".join(url[1:len(url)+1])
		else:
			url = url[0]

		temp = url.split(":")
		if(len(temp) == 2):
			temp[1] = temp[1].split("/", 1)
			if(len(temp[1]) == 2):

				(host, port, path) = (temp[0], temp[1][0], temp[1][1])
			else:
				(host, port, path) = (temp[0], temp[1],  "/")
		else:
			temp[0] = temp[0].split("/", 1)
			if(len(temp[0]) == 2):
				(host, port, path) = (temp[0][0], 80, temp[0][1])
			else:
				(host, port, path) = (temp[0][0], 80, "/")
		if(path and path[0] != "/"):
			path = "/" + path
		else:
			path = "/"
		return (self.rmList(host), int(self.rmList(port)), self.rmList(path))		
		

	def connect(self, host, port, request):
		clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		clientSocket.connect((host, port))
		clientSocket.sendall(request)
		return clientSocket

	def get_code(self, data):
		return int(data.split(" ")[1])

	def get_headers(self,data):
		return None

	def get_body(self, data):
		data = data.split("\n\n")
		if(len(data) == 1):
			data = self.rmList(data).split("\r\n\r\n")
		#Take all data after the first \r\n\r\n as it could potentially apear in the body itself:
		body = "".join(data[1:len(data)+1])		
		return body

	# read everything from the socket
	def recvall(self, sock):

		sock.settimeout(2.0)
		buffer = bytearray()
		done = False
		while not done:
			try:
				part = sock.recv(1024)
			except:
				part = None
				done = True
			if (part):
				buffer.extend(part)
			else:
				done = not part
		return str(buffer)

	def formatRequest(self, command, host, port, path="/", body=None):
		protocol = "HTTP/1.1"
		UA = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"
		Accept = "*/*"
		body = self.formatBody(body)
		request = "%s %s %s\nHost: %s:%s\nUser-Agent: %s\nAccept: %s%s" % (command, path, protocol, host, port, UA, Accept, body)
		print("-----------------------------\n\nREQUEST SENT: \n%s\n---------------------------------\n" % request)
		return request

	def formatBody(self, body):
		if(body == None):
			return "\r\n\r\n"
		body = urllib.urlencode(body)
		return "\nContent-Type: application/x-www-form-urlencoded\nContent-Length: %d\r\n\r\n%s" % (len(body), body)

	def GET(self, url, args=None):
		(host, port, path) = self.get_host_port(url)
		request = self.formatRequest("GET", host, port, path, None)
		clientSocket = self.connect(host, port, request)
		recv = self.recvall(clientSocket)
		code = self.get_code(recv)
		body = self.get_body(recv)
		return HTTPResponse(code, body)

	def POST(self, url, args=None):
		(host, port, path) = self.get_host_port(url)
		request = self.formatRequest("POST", host, port, path, args)
		clientSocket = self.connect(host, port, request)
		recv = self.recvall(clientSocket)
		code = self.get_code(recv)
		body = self.get_body(recv)
		return HTTPResponse(code, body)

	def command(self, command, url, args=None):
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
		print client.command( sys.argv[1], sys.argv[2] )
	else:
		print client.command( command, sys.argv[1] )    



