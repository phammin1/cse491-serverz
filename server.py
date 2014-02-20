#!/usr/bin/env python
# Minh Pham
# CSE 491

import random, socket, time
from urlparse import urlparse  # credit to Jason Lefler code
import signal # to control execution time
import StringIO # for string buffer
from app import make_app # for making an app
from wsgiref.validate import validator
from sys import stderr
import ServerEnv

# buffer size for conn.recv
BuffSize = 128

# timeout for conn.recv (in seconds)
ConnTimeout = .1

# A template of Environment
EnvFile = 'env.txt'

def main(socketModule = None):
    if socketModule == None:
        socketModule = socket

    s = socketModule.socket()         # Create a socket object
    host = socketModule.getfqdn() # Get local machine name
    port = random.randint(8000,8009)
    ipAddress = socketModule.gethostbyname(host)
    s.bind((host, port))        # Bind to the port
    
    print 'Starting server on', ipAddress, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        conn, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(conn, host, port)

# raise error when time out
def signal_handler(signum, frame):
    raise Exception("Timed out!")

def handle_connection(conn, host='fake', port=8080):
    # start_response function used in make_app
    # credit to Ben Taylor and Josh Shadik
    def start_response(status, resHeaders, exc_info=None):
        conn.send('HTTP/1.0 %s\r\n' % (status))
        for header in resHeaders:
            conn.send('%s: %s\r\n' % header)
        conn.send('\r\n')

    # Create a default environ to avoid code breaking
    defaultEnv = ServerEnv.DefaultEnv(host, port)
            
    reqData = getData(conn)
    reqEnv = createEnv(reqData, defaultEnv)
    resPage = validator(make_app())(reqEnv, start_response)
    
    for svrRes in resPage:
        conn.send(svrRes)
    resPage.close()
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

# create environment dictionary from request data and a default environment
def createEnv(reqData, defaultEnv):
    if reqData == '':
        return ServerEnv.Error404Env # evil empty request
    
    buf = StringIO.StringIO(reqData)
    line = buf.readline()

    # some default value to avoid code breaking
    env = defaultEnv.copy()
    env['REQUEST_METHOD'] = line.split()[0]
    
    try:
        uri = line.split()[1]
    except IndexError:
        return ServerEnv.Error404Env # more evil request    
    env['PATH_INFO'] = uri.split('?',1)[0]
    if "?" in uri:
        env['QUERY_STRING'] = uri.split('?',1)[1]

    # putting headers data to environment dict
    while True:
        line = buf.readline()
        if line == '\r\n' or line == '':
            break # empty line = end of headers section
        if ': ' in line:
            key, value = line.strip('\r\n').split(": ",1)
            key = key.upper().replace('-','_')
            env[key] = value
        else:
            return ServerEnv.Error404Env

    env['wsgi.input'] = buf
    return env

if __name__ == '__main__':
    main()
