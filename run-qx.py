import socket
import random

### here is the code needed to create a WSGI application interface to
### a Quixote app:

import quixote
from quixote.demo import create_publisher
from quixote.demo.mini_demo import create_publisher
from quixote.demo.altdemo import create_publisher

p = create_publisher()
wsgi_app = quixote.get_wsgi_app()

### now that we have a WSGI app, we can run it in the WSGI reference server:

from wsgiref.simple_server import make_server

host = socket.getfqdn() # Get local machine name
port = random.randint(8000, 9999)
p.is_thread_safe = True                 # hack...
httpd = make_server('', port, wsgi_app)
print "Serving at http://%s:%d/..." % (host, port,)
httpd.serve_forever()

