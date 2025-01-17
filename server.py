#  coding: utf-8 
import socketserver, os, socket
from urllib.parse import urlparse
import mimetypes
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime



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

PATH_PRIFIX = 'www'

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.recv_data(self.request)

        if self.data == b'':
            return
        #print ("Got a request of: %s\n" % self.data)
        data = self.data.decode('utf-8')
        data = data.split('\r\n')
        http_method, url_proto0, http_version = data[0].split()

        if http_method != "GET":
            response_version = http_version
            response_status = '405'
            response_status_text = 'Method Not Allowed'

            # sending all this stuff
            r = '%s %s %s\r\n' % (response_version, response_status, response_status_text)
            self.request.sendall((bytearray(r,'utf-8')))
            return
        url_proto = url_proto0.replace(' ', '')
        

        url_proto = PATH_PRIFIX + url_proto0
        
        url_path = urlparse(url_proto).path

        url_path = os.path.realpath(url_path)
        cwd = os.getcwd()+'/www'
        cwd = os.path.realpath(cwd)
        check = os.path.commonprefix([url_path, cwd]) == cwd

        if not check:
            self.send_404(http_version)
            return

        url_path = urlparse(url_proto).path

        if url_path[-1] == '/':
            url_path += 'index.html'
        else:
            if os.path.isdir(url_path):
                url_proto += '/'
                url_path = 'Location: ' + url_proto0 + '\r\n'
                response_version = http_version
                response_status = '301'
                response_status_text = 'Moved Permanently'
                now = datetime.now()
                stamp = mktime(now.timetuple())
                date =  format_date_time(stamp)
                date = 'Date: ' + date

                # sending all this stuff
                a = '%s %s %s\r\n' % (response_version, response_status, response_status_text)
                a = a + date + '\r\n'
                self.request.sendall(bytearray(a,'utf-8'))
                self.request.sendall(bytearray(url_path,'utf-8'))
                self.request.sendall(bytearray('Cache-Control: no-cache\r\n','utf-8'))
                return


        try:
            with open(url_path, 'r') as f:
                data = f.read()
                mime = mimetypes.guess_type(url_path)[0]
                if mime == None:
                    mime = 'application/octet-stream'
                response_version = http_version
                response_status = '200'
                response_status_text = 'OK'
                content_type = 'Content-type: ' + mime + '; charset=utf-8'
                content_length = 'Content-Length: ' + str(len(data))
                now = datetime.now()
                stamp = mktime(now.timetuple())
                date =  format_date_time(stamp)
                date = 'Date: ' + date
                connection = 'Connection: close'


                # sending all this stuff
                header = '%s %s %s  \r\n' % (response_version, response_status, response_status_text)

                header += content_type + '\r\n' + content_length + '\r\n' + connection + '\r\n' + date + '\r\n' + '\r\n'

                message = header + data
                self.request.sendall(bytearray(message, 'utf-8'))
                #print(message)
                
                #self.request.sendall(data)
        except Exception as e:
            self.send_404(http_version)

        # print(http_method)
        # print(url_path)
        # print(http_version)

    def send_404(self, http_version):
        response_version = http_version
        response_status = '404'
        response_status_text = 'Not Found' # this can be random
        now = datetime.now()
        stamp = mktime(now.timetuple())
        date =  format_date_time(stamp)
        date = 'Date: ' + date

        # sending all this stuff
        d = '%s %s %s\r\n' % (response_version, response_status, response_status_text)
        d += date + '\r\n'
        self.request.sendall((bytearray(d,'utf-8')))
    
    def finish(self):
        self.request.close()
    
    def recv_data(self, s):
        s.settimeout(0.1)
        full_data=b''
        try:
            while True:

                data = s.recv(1024)
                if not data or data == b'':
                    break
                full_data += data.strip()
        except socket.timeout:
            return full_data
        return full_data

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
