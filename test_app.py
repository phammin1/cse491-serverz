# Minh Pham
# CSE 491

import app
import envTemplates

# List of pages have been implemented
PageList = ['index', 'content', 'form', 'formPost', 'environ']

class FakeServer(object):
   """
   A fake server class that mimic WSGI simple_server for testing
   """
   def __init__(self, app=app.make_app()):
       self.env = envTemplates.DefaultEnv()
       self.status = ''
       self.headers = []
       self.app = app
       self.response = []

   def start_response(self, status='', headers=[]):
       self.status = status
       self.headers = headers

   def isOkay(self):
       return self.status == '200 OK'

   def request(self,reqString):
       self.env['REQUEST_METHOD'] = reqString.split()[0]
       uri = reqString.split()[1]
       self.env['PATH_INFO'] = uri.split('?',1)[0]
       self.env['QUERY_STRING'] = uri.split('?',1)[-1]
       self.response = self.app(self.env, self.start_response).next()

   # print full response with status and headers
   def info(self):
       info = "Status code:%s\n" %(self.status)
       info += "Headers: %s\n" %(repr(self.headers))
       info += "Response: %s\n" %(repr(self.response))
       return info
   
def test_index():
    reqString = "GET / HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.isOkay(), "Not Okay\n" + server.info()
    assert 'Hello' in server.response, "Wrong page\n" + server.info()

def test_index_html():
    reqString = "GET /index.html HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.isOkay(), "Not Okay\n" + server.info()
    assert 'Hello' in server.response, "Wrong page\n" + server.info()
    
def test_all_normal_page():
    server = FakeServer()

    for page in PageList:
        reqString = "GET /" + page + " HTTP/1.0\r\n\r\n"
        server.request(reqString)

        assert server.isOkay(), "Not Okay\n" + server.info()
        assert page.capitalize() in server.response,\
            "Wrong page:" + page.capitalize() + '\n' + server.info()

def test_404_get():
    reqString = "GET /fake HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.status == '404 Not Found', "Not Found\n" + server.info()
        
def test_favicon():
    reqString = "GET /favicon.ico HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.isOkay(), "Not Okay\n" + server.info()

def test_fake_file():
    reqString = "GET /fake.file HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.status == '404 Not Found', "Not Found\n" + server.info()

def test_submit_get():
    reqString = "GET /submit?firstname=Minh&lastname=Pham HTTP/1.0\r\n\r\n"

    server = FakeServer()
    server.request(reqString)

    assert server.isOkay(), "Not Okay\n" + server.info()
    assert 'Minh Pham' in server.response, "Wrong page\n" + server.info()
