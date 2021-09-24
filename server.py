#  coding: utf-8 
import socketserver
from os import listdir
from os.path import isdir

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        '''

        '''
        # Capture and parse the request
        request = self.request.recv(1024).strip()
        self.parse_request(request)

        # Get response content
        content = self.get_content()

        # Send response
        self.respond(content)
    
    def parse_request(self, request):
        # Decode request and split by newlines
        request = request.decode("utf-8").split("\r\n")

        # Initialize data as a dictionary
        self.data = {"Method": request[0].split(" ")[0], "Path": request[0].split(" ")[1]}

        # Add key-value pairs for all headers
        for i in range(1, len(request)):
            header = request[i].split(": ", 1)
            if len(header) > 1:
                self.data[header[0]] = header[1]
            else:
                self.data[header[0]] = header[0]

    def respond(self, content):
        # If there is a 301 error, redirect by providing correct location
        location = ""
        if "301" in content["status"]:
            path = self.data["Path"]
            host = self.data["Host"]
            location = f"Location: http://{host}{path}/\r\n"

        # Deal with cases where the mime type is not dealt with
        content_type = ""
        if content['type']:
            content_type = f"Content-Type: {content['type']}\r\n"
        
        response = f"HTTP/1.1 {content['status']}\r\n{location}Content-Length: {content['length']}\r\n{content_type}\r\n{content['string']}"

        # Send response
        self.request.sendall(bytearray(response, "utf-8"))

    def get_content(self):
        # Get path and method from data
        path = self.data["Path"]
        method = self.data["Method"]
 
        # Handle 405 Errors
        if method.upper() != "GET":
            return self.error_content("405 Method Not Allowed")

        # Parse the path
        path_list = path.split("/")

        # Ignore / at the beginning of the path
        if path_list[0] == "":
            path_list.pop(0)

        # If there is a trailing slash, go to index
        if path_list[-1] == "":
            path_list[-1] = "index.html"

        curr_path = "www/"

        # Handle 404 Errors
        # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        for i in range(0, len(path_list)):
            if path_list[i] not in listdir(curr_path):
                return self.error_content("404 Not Found")
            curr_path += path_list[i]
            if i != len(path_list) - 1:
                curr_path += "/"

        # Handle 301 Errors
        if isdir(curr_path):
            return self.error_content("301 Moved Permanently")

        # Get file content
        file = open(curr_path, "r")
        content_string = file.read()
        file.close()

        # Get mime datatype
        extension = curr_path.split(".")[-1]
        mimetype = None
        if extension in ("html", "css"):
            mimetype = f"text/{extension}"

        # Format content in a dict
        content = {
            "status": "200 OK",
            "length": len(content_string),
            "type": mimetype,
            "string": content_string
        }

        return content
    
    def error_content(self, status_code):
        # Create a basic HTML page with the error
        content_string = f"""<!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{status_code}</title>
                </head>
                <body>
                    {status_code}
                </body>
            </html>"""
        
        # Format content in a dict
        content = {
            "status": status_code,
            "length": len(content_string),
            "type": "text/html",
            "string": content_string
        }
        
        return content

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
