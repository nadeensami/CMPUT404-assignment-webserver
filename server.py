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
        # Decode request and split by newlines
        self.data = self.request.recv(1024).strip().decode("utf-8").split("\r\n")        
        # print ("Got a request of: %s\n" % self.data)

        # Use the request line to get the method and path
        request_line = self.data[0].split(" ")
        method = request_line[0]
        path = request_line[1]

        if method.upper() != "GET":
            # Handle 405 Errors
            content = self.error_content("405 Method Not Allowed")
        else:
            content = self.get_content(path)

        self.respond(content)

    def respond(self, content):
        location = ""
        if "301" in content["status"]:
            path = self.data[0].split(" ")[1]
            host = self.data[1].split(" ")[1]
            location = f"Location: http://{host}{path}/\r\n"
        
        response = f"""HTTP/1.1 {content['status']}\r\n{location}Content-Length: {content['length']}\r\nContent-Type: {content['type']}\r\n\r\n{content['string']}"""
        
        # print(f"Response: {response}")

        self.request.sendall(bytearray(response, "utf-8"))

    def get_content(self, path):
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
            # Deal with 404 error
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
        mime_type = self.get_mime_type(extension)

        # Format content in a dict
        content = {"status": "200 OK", 
                "length": len(content_string), 
                "type": mime_type, 
                "string": content_string}

        return content
    
    def get_mime_type(self, extension):
        if extension in ("html", "css"):
            return f"text/{extension}"
    
    def error_content(self, status_code):
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
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
        
        content = {"status": status_code, 
                "length": len(content_string), 
                "type": "text/html", 
                "string": content_string}
        
        return content

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
