import server
import jinja2

jinjaTemplate = './templates'

okay_header = 'HTTP/1.0 200 OK' 

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False
        jLoader = jinja2.FileSystemLoader(jinjaTemplate)
        self.jEnv = jinja2.Environment(loader=jLoader)

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

    def env(self):
        return self.jEnv

    def isOkay(self):
        return self.header() == okay_header

    def header(self):
        return self.sent.split('\r\n')[0]

# Test a basic GET call.

def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Hello' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_handle_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Content' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)
    
def test_handle_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'File' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_handle_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Image' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_handle_form():
    conn = FakeConnection("GET /form HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Form' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_get_submit():
    conn = FakeConnection("GET /submit?firstname=Minh&lastname=Pham&submit=Submit+Query HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())
    
    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Minh Pham' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_get_submit_empty():
    conn = FakeConnection("GET /submit HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())
    
    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'No Name' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_form_post():
    conn = FakeConnection("GET /formPost HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'POST' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_404_post():
    conn = FakeConnection("POST /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.header() == 'HTTP/1.0 404 Not Found', 'Got: %s' % (repr(conn.sent),)

def test_404_fake():
    conn = FakeConnection("FAKE /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.header() == 'HTTP/1.0 404 Not Found', 'Got: %s' % (repr(conn.sent),)

def test_404_get():
    conn = FakeConnection("GET /fake HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.header() == 'HTTP/1.0 404 Not Found', 'Got: %s' % (repr(conn.sent),)

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
	'Content-Length: 420\r\n' +\
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
	'-----------------------------10925359777073771901781915428--\r\n'
    conn = FakeConnection(reqString)
    server.handle_connection(conn, conn.env())

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
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Minh Pham' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_post_submit_empty():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n\r\n")
    server.handle_connection(conn, conn.env())

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'No Name' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)
