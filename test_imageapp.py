import server
import jinja2
import imageapp
import quixote
import imageTemplate

okay_header = 'HTTP/1.0 200 OK'

bad_request_header ='HTTP/1.0 400 Bad Request'

redirect_header = 'HTTP/1.0 302 Moved Temporarily'

not_found_header = 'HTTP/1.0 404 Not Found'

# List of pages have been implemented
PageList = ['', 'search', 'image_list', 'image', 'upload_image']

imageapp.setup()
imageapp.create_publisher()
theApp = quixote.get_wsgi_app()

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

    def isRedirect(self):
        return redirect_header in self.status()

    def is404(self):
        return not_found_header in self.status()

    def status(self):
        return self.sent.split('\r\n')[0]
    
    def headers(self):
        return self.sent.split('\r\n\r\n')[0]

    def content(self):
        return self.sent.split('\r\n\r\n')[1]

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

class FakeFile(object):
    def __init__(self, fileDir):
        self.base_filename = fileDir.split('/')[-1]
        self.file = open(fileDir, 'rb')

    def read(self, intParam):
        return self.file
    
# Test main for increased coverage
def test_main():
    fakemodule = FakeSocketModule()

    success = False
    try:
        server.main(fakemodule)
    except AcceptCalledMultipleTimes:
        success = True

    assert success, "something went wrong"

def handle_conn(conn):
    server.handle_connection(conn, anApp=theApp)
    
# Test a basic GET call.
def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    handle_conn(conn)

    assert conn.isOkay(), 'Got: %s' % (repr(conn.sent),)
    assert 'Upload an image' in conn.sent, 'Wrong page: %s' % (repr(conn.sent),)

def test_all_normal_page():
    for page in PageList:
        reqString = "GET /" + page + " HTTP/1.0\r\n\r\n"
        conn = FakeConnection(reqString)
        handle_conn(conn)

        assert conn.isOkay(), 'Page: %s \n %s' % (page,repr(conn.sent),)

def test_image_raw():
    reqString = "GET /image_raw?i=0 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    imgData = open('imageapp/favicon.ico', 'rb').read()
    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert conn.content() == imgData, "Wrong image raw"

def test_image_detail():
    reqString = "GET /image_detail?i=0&f=file_name HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'fav.ico' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)

def test_evil_image_detail():
    reqString = "GET /image_detail?i=0 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'revalidate' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)

def test_evil_image_detail2():
    reqString = "GET /image_detail?i=0&f=fake HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'revalidate' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)
    
def test_search_result():
    reqString = "GET /search_result?file=fav&description= HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'fav.ico' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)

def test_add_comment():
    reqString = "GET /add_comment?user=Minh&comment=Awesome" +\
        "&time=0 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert "success" in conn.sent, 'Fail:  %s' % (repr(conn.sent),)
    assert "Awesome" in conn.sent, \
        "Comment wasn't added: %s"  % (repr(conn.sent),)

def test_refresh_comment():
    reqString = "GET /add_comment?user=&comment=Awesome" +\
        "&time=0 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert "success" in conn.sent, 'Fail:  %s' % (repr(conn.sent),)
    assert "Awesome" in conn.sent, \
        "Comment wasn't added: %s"  % (repr(conn.sent),)

def test_evil_comment():
    reqString = "GET /add_comment?user=Minh&comment=Awesome" +\
        "&time=abc HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert "fail" in conn.sent, 'Fail:  %s' % (repr(conn.sent),)

def test_empty_comment():
    reqString = "GET /add_comment HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert "fail" in conn.sent, 'Fail:  %s' % (repr(conn.sent),)

def test_max_time_comment():
    reqString = "GET /add_comment?user=&comment=Awesome" +\
        "&time=1e20 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert "success" in conn.sent, 'Fail:  %s' % (repr(conn.sent),)
    assert '"result": []' in conn.sent, \
        "Result not empty: %s"  % (repr(conn.sent),)
    
def test_jquery():
    reqString = "GET /jquery HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    
def test_404():
    reqString = "GET /fake HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.is404(), 'Found something:  %s' % (repr(conn.sent),)

def test_image_out_of_range():
    reqString = "GET /image?i=1000 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)

def test_image_negative():
    reqString = "GET /image?i=-1 HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'fav.ico' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)

def test_image_fake():
    reqString = "GET /image?i=fake HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isOkay(), 'Not Okay:  %s' % (repr(conn.sent),)
    assert 'fav.ico' in conn.sent, 'Wrong info:  %s' % (repr(conn.sent),)

#def test_upload_receive():
 #   reqString = imageTemplate.postImageRequest
  #  conn = FakeConnection(reqString)
   # handle_conn(conn)

    #assert conn.isRedirect(), 'Not a Redirect:  %s' % (repr(conn.sent),)
    
def test_upload_receive_evil():
    reqString = "GET /upload_receive HTTP/1.0\r\n\r\n"
    conn = FakeConnection(reqString)
    handle_conn(conn)

    assert conn.isRedirect(), 'Not a Redirect:  %s' % (repr(conn.sent),)
