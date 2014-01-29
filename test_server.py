import server

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False

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

# Test a basic GET call.

def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Hello</h1>' + \
                      '<a href="/content">Content</a><br></br>' + \
                      '<a href="/file">File</a><br></br>' + \
                      '<a href="/image">Image</a><br></br>' + \
                      '<a href="/form">Form</a><br></br>' +\
                      '<a href="/formPost">Form (Post)</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Content</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    
def test_handle_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>File</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Image</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_form():
    conn = FakeConnection("GET /form HTTP/1.0\r\n\r\n")
    expected_return ='HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Form</h1>" + \
                     "<form action='/submit' method='GET'>" +\
                     "<input type='text' name='firstname'><br></br>" +\
                     "<input type='text' name='lastname'><br></br>" +\
                     "<input type='submit' name='submit'><br></br>" +\
                     "</form>" +\
                     '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    
def test_handle_post():
    conn = FakeConnection("POST / HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>POST method</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_submit():
    conn = FakeConnection("GET /submit?firstname=Minh&lastname=Pham&submit=Submit+Query HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>Hello Minh Pham</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_post_submit():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<h1>(Post) Hello No Name</h1>' + \
                      '<a href="/">Home</a><br></br>' +\
                      'This is Minh\'s Web server.'

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_post_form():
    conn = FakeConnection("GET /formPost HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Form Post</h1>" + \
                     "<form action='/submit' method='POST'>" +\
                     "<input type='text' name='firstname'><br></br>" +\
                     "<input type='text' name='lastname'><br></br>" +\
                     "<input type='submit' name='submit'><br></br>" +\
                     "</form>" +\
                     '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)    
