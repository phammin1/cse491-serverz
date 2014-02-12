#!/usr/bin/env python
# Minh Pham
# CSE 491

import random, socket, time
from urlparse import urlparse  # credit to Jason Lefler code
import signal # to control execution time
import StringIO # for string buffer
from app import make_app # for making an app

# buffer size for conn.recv
BuffSize = 128

# timeout for conn.recv (in seconds)
ConnTimeout = .1

def main(socketModule = None):
    if socketModule == None:
        socketModule = socket

    s = socketModule.socket()         # Create a socket object
    host = socketModule.getfqdn() # Get local machine name
    port = random.randint(8000,8009)
    s.bind((host, port))        # Bind to the port
    
    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        conn, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(conn)

# raise error when time out
def signal_handler(signum, frame):
    raise Exception("Timed out!")

def handle_connection(conn):
    # start_response function used in make_app
    # credit to Ben Taylor
    def start_response(status, headers):
        headRes = 'HTTP/1.0 ' + status + '\r\n'
        for header in headers:
            k, v = header
            headRes += k + ': ' + v + '\r\n'
        headRes += '\r\n'
        conn.send(headRes)
        
    reqData = getData(conn)
    reqEnv = createEnv(reqData)
    resPage = make_app()(reqEnv, start_response)
    
    for svrRes in resPage:
        conn.send(svrRes)
    conn.close()

# handle getting data from connection with arbitrary size
def getData(conn):
    # Note: can use global reqData to get rid of error
    reqData = ""
    # signal is used to control execution time
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, ConnTimeout, ConnTimeout) # set timeout

    try:
        while True:
            reqData += conn.recv(BuffSize)
    except Exception, msg:
        signal.alarm(0) # turn off signal
    return reqData

# create environment dictionary from request data
def createEnv(reqData):
    if reqData == '':
        return create404Env(reqData) # evil empty request
    
    buf = StringIO.StringIO(reqData)
    line = buf.readline()

    # some default value to avoid code breaking
    env = {'REQUEST_METHOD' : line.split()[0],\
               'QUERY_STRING' : '',\
               'CONTENT_TYPE' :'application/x-www-form-urlencoded',\
               'CONTENT_LENGTH' : '0'}
    try:
        uri = line.split()[1]
    except IndexError:
        return create404Env(reqData) # more evil request
    
    env['PATH_INFO'] = uri.split('?',1)[0]
    if "?" in uri:
        env['QUERY_STRING'] = uri.split('?',1)[1]

    while True:
        line = buf.readline()
        if line == '\r\n' or line == '':
            break # empty line = end of headers section
        key, value = line.strip('\r\n').split(": ",1)
        key = key.upper().replace('-','_')
        env[key] = value

    env['wsgi.input'] = buf
    return env

# Create a 404 environment
def create404Env(reqData):
    env = {'REQUEST_METHOD' : 'GET',\
               'QUERY_STRING' : '',\
               'PATH_INFO': '/fakeabcz',\
               'wsgi.input': None}

    print 'Environ: ',env
    
    return env
    
if __name__ == '__main__':
    main()
