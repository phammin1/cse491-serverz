import server
import jinja2

okay_header = 'HTTP/1.0 200 OK'

bad_request_header ='HTTP/1.0 400 Bad Request'

# List of pages have been implemented
PageList = ['index', 'content', 'form', 'formPost', 'environ']

class AcceptCalledMultipleTimes(Exception):
    pass

class FakeSocketModule(object):
    def getfqdn(self):
        return "fakehost"

    def gethostbyname(self, host):
        return "0.fake.0.host"

    def socket(self):
        return FakeConnection("")
    
class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False
        self.n_times_accept_called = 0

    def recv(self, n):
        if n > len(self.to_recv):
            r = self.to_recv
            self.to_recv = ""
            return r
            
        r, self.to_recv = self.to_recv[:n], self.to_recv[n:]
        return r

    def send(self, s):
        self.sent += s

    def close(self):
        self.is_closed = True

    def isOkay(self):
        return okay_header in self.status()

    def isBad(self):
        return bad_request_header in self.status()

    def status(self):
        return self.sent.split('\r\n')[0]
    
    def headers(self):
        return self.sent.split('\r\n\r\n')[0]

    def bind(self, param):
        (host, port) = param
    
    def listen(self, n):
        if n != 5:
            raise Exception("n should be five you dumby")

    def accept(self):
        if self.n_times_accept_called > 1:
            raise AcceptCalledMultipleTimes("stop calling accept, please")
        self.n_times_accept_called += 1
        
        c = FakeConnection("")
        return c, ("noclient", 32351)

# Test main for increased coverage
def test_main():
    fakemodule = FakeSocketModule()

    success = False
    try:
        server.main(fakemodule)
    except AcceptCalledMultipleTimes:
        success = True

    assert success, "something went wrong"
    
# Test a basic GET call.
def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Hello' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_all_normal_page():
    for page in PageList:
        reqString = "GET /" + page + " HTTP/1.0\r\n\r\n"
        conn = FakeConnection(reqString)
        server.handle_connection(conn)

        assert conn.isOkay(), 'Not Okay: %s' % (repr(conn.sent),)
        assert page.capitalize() in conn.sent,\
           'Wrong page %s: %s' % (page,repr(conn.sent),)

def test_get_submit():
    conn = FakeConnection("GET /submit?firstname=Minh&lastname=Pham&submit=Submit+Query HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)
    
    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Minh Pham' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_get_submit_empty():
    conn = FakeConnection("GET /submit HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)
    
    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'No Name' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_404_post():
    conn = FakeConnection("POST /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.status() == 'HTTP/1.0 404 Not Found',\
        'Got: %s' % (repr(conn.sent),)

def test_404_options():
    conn = FakeConnection("OPTIONS /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.status() == 'HTTP/1.0 404 Not Found',\
        'Got: %s' % (repr(conn.sent),)

def test_404_get():
    conn = FakeConnection("GET /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.status() == 'HTTP/1.0 404 Not Found',\
        'Got: %s' % (repr(conn.sent),)

def test_post_submit_multi():
    reqString = 'POST /submit HTTP/1.1\r\n' +\
	'Host: arctic.cse.msu.edu:9853\r\n' +\
	'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20131030 Firefox/17.0 Iceweasel/17.0.10\r\n' +\
	'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
	'Accept-Language: en-US,en;q=0.5\r\n' +\
	'Accept-Encoding: gzip, deflate\r\n' +\
	'Connection: keep-alive\r\n' +\
	'Referer: http://arctic.cse.msu.edu:9853/formPost\r\n'+\
	'Content-Type: multipart/form-data; boundary=---------------------------10925359777073771901781915428\r\n' +\
	'Content-Length: 418\r\n' +\
	'\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n' +\
	'Content-Disposition: form-data; name="firstname"\r\n' +\
	'\r\n' +\
	'Minh\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n' +\
	'Content-Disposition: form-data; name="lastname"\r\n' +\
	'\r\n' +\
	'Pham\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n' +\
	'Content-Disposition: form-data; name="submit"\r\n' +\
	'\r\n' +\
	'Submit Query\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n'
    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Minh Pham' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_post_submit_app():
    reqString = 'POST /submit HTTP/1.1\r\n' +\
	'Host: arctic.cse.msu.edu:9176\r\n' +\
	'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20131030 Firefox/17.0 Iceweasel/17.0.10\r\n' +\
	'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
	'Accept-Language: en-US,en;q=0.5\r\n' +\
	'Accept-Encoding: gzip, deflate\r\n' +\
	'Connection: keep-alive\r\n' +\
	'Referer: http://arctic.cse.msu.edu:9176/formPost\r\n' +\
	'Content-Type: application/x-www-form-urlencoded\r\n' +\
	'Content-Length: 48\r\n' +\
	'\r\n' +\
	'firstname=Minh&lastname=Pham&submit=Submit+Query\r\n'

    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Minh Pham' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_post_submit_empty():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'No Name' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_favicon():
    conn = FakeConnection("GET /favicon.ico HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.isOkay(), 'Not Okay: %s' % (repr(conn.headers()),)

def test_fake_file():
    conn = FakeConnection("GET /fake.file HTTP/1.0\r\n\r\n")
    server.handle_connection(conn)

    assert conn.status() == 'HTTP/1.0 404 Not Found',\
        'Got: %s' % (repr(conn.sent),)
    
def test_evil_empty():
    conn = FakeConnection("")
    server.handle_connection(conn)

    assert conn.isBad(), 'Got: %s' % (repr(conn.sent),)
    assert 'Plain evil' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_evil_get():
    conn = FakeConnection("GET")
    server.handle_connection(conn)

    assert conn.isBad(), 'Got: %s' % (repr(conn.sent),)
    assert 'Plain evil' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

# evil content-length:48 (no space)
def test_evil_header():
    reqString = 'POST /submit HTTP/1.1\r\n' +\
	'Content-Type: application/x-www-form-urlencoded\r\n' +\
	'Content-Length:48\r\n' +\
	'\r\n' +\
	'firstname=Minh&lastname=Pham&submit=Submit+Query\r\n'

    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isBad(), 'Got: %s' % (repr(conn.sent),)
    assert 'wrong headers' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

# test a large file to see if it reject
def test_evil_large_file():
    reqString = 'POST /submit HTTP/1.1\r\n' +\
	'Host: arctic.cse.msu.edu:9853\r\n' +\
	'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20131030 Firefox/17.0 Iceweasel/17.0.10\r\n' +\
	'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
	'Accept-Language: en-US,en;q=0.5\r\n' +\
	'Accept-Encoding: gzip, deflate\r\n' +\
	'Connection: keep-alive\r\n' +\
	'Referer: http://arctic.cse.msu.edu:9853/formPost\r\n'+\
	'Content-Type: multipart/form-data; boundary=---------------------------10925359777073771901781915428\r\n' +\
	'Content-Length: 100000001\r\n' +\
	'\r\n' +\
	'Submit Query\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n'
    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isBad(), 'Got: %s' % (repr(conn.headers()),)
    assert 'too big' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

# test connection time out
def test_conn_timeout():
    reqString = 'POST /submit HTTP/1.1\r\n' +\
	'Host: arctic.cse.msu.edu:9853\r\n' +\
	'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20131030 Firefox/17.0 Iceweasel/17.0.10\r\n' +\
	'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
	'Accept-Language: en-US,en;q=0.5\r\n' +\
	'Accept-Encoding: gzip, deflate\r\n' +\
	'Connection: keep-alive\r\n' +\
	'Referer: http://arctic.cse.msu.edu:9853/formPost\r\n'+\
	'Content-Type: multipart/form-data; boundary=---------------------------10925359777073771901781915428\r\n' +\
	'Content-Length: 891\r\n' +\
	'\r\n' +\
	'Submit Query\r\n' +\
	'-----------------------------10925359777073771901781915428\r\n'
    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isBad(), 'Got: %s' % (repr(conn.headers()),)
    assert 'Timeout' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

# test a large jpg file to see if it slows down
def test_large_jpg():
    reqString = 'GET /large.jpg HTTP/1.0\r\n\r\n'
    conn = FakeConnection(reqString)
    server.handle_connection(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.headers()),)
