#!/usr/bin/env python
# Minh Pham
# CSE 491

import random, socket, time
from urlparse import urlparse  # credit to Jason Lefler code
import signal # to control execution time
import StringIO # for string buffer
from app import make_app # for making an app
from wsgiref.validate import validator # validating server side
import argparse # for command line argument
import envTemplates # for some default environment
from appChooser import choose_app, AppChoices # choosing app

# Constant
# buffer size for conn.recv
BuffSize = 128

# timeout for conn.recv (in seconds)
ConnTimeout = 3

# Max File size to be receive from the server (in byte)
MaxFileSize = 1e8

def main(socketModule = None):
    # for testing main
    if socketModule == None:
        socketModule = socket
        # choose app based on system argument
        args = parse_sys_arg()
        myApp = choose_app(args.app)
        # choose port number
        port = args.port
    else:
        myApp = choose_app('default')
        port = 0

    s = socketModule.socket()         # Create a socket object
    host = socketModule.getfqdn() # Get local machine name
    
    ipAddress = socketModule.gethostbyname(host)
    s.bind((host, port))        # Bind to the port
    
    print 'Starting server on', ipAddress, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'

    try:
        while True:
            # Establish connection with client.    
            conn, (client_host, client_port) = s.accept()
            print 'Got connection from', client_host, client_port
            handle_connection(conn, host, port, myApp)
    except KeyboardInterrupt:
        print "\nExiting server...\n"

# raise error when time out
def signal_handler(signum, frame):
    raise Exception("Timed out!")

def handle_connection(conn, host='fake', port=0, anApp=make_app()):
    # start_response function used in make_app
    # credit to Ben Taylor and Josh Shadik
    def start_response(status, resHeaders, exc_info=None):
        conn.send('HTTP/1.0 %s\r\n' % (status))
        for header in resHeaders:
            conn.send('%s: %s\r\n' % header)
        conn.send('\r\n')

    # Create a default environ to avoid code breaking
    defaultEnv = envTemplates.DefaultEnv(host, port)
            
    reqEnv = getData(conn, defaultEnv)
    #myApp = validator(anApp)
    myApp = anApp
    resPage = myApp(reqEnv, start_response) # normal server
    
    for svrRes in resPage:
        conn.send(svrRes)

    #resPage.close()
    conn.close()

# handle getting data from connection with arbitrary size
# return an environment dictionary
def getData(conn, defaultEnv):
    # signal is used to control execution time
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(ConnTimeout) # set timeout
    
    env = envTemplates.Error404Env
    try:
        env = createEnv(conn, defaultEnv)
    except Exception, msg:
        print "Connection Timeout:", msg
        env = envTemplates.Error400Env("Timeout")

    signal.alarm(0) # turn off signal

    return env

# create environment dictionary from connection and a default environment
def createEnv(conn, defaultEnv):
    # Credit to Ben Taylor for parsing request
    # Start reading in data from the connection
    reqRaw = conn.recv(1)
    while reqRaw[-4:] != '\r\n\r\n':
        new = conn.recv(1)
        if new == '':
            return envTemplates.Error400Env("Plain evil")
        else:
            reqRaw += new
    
    # some default value to avoid code breaking
    env = defaultEnv.copy()
    
    req, data = reqRaw.split('\r\n',1)
    env['REQUEST_METHOD'] = req.split(' ',1)[0]
    
    try:
        uri = req.split()[1]
    except IndexError:
        return envTemplates.Error400Env("No path in request") # evil
    
    env['PATH_INFO'] = uri.split('?',1)[0]
    if "?" in uri:
        env['QUERY_STRING'] = uri.split('?',1)[1]

    # putting headers data to environment dict
    for line in data.split('\r\n')[:-2]:
        if ': ' in line:
            key, value = line.strip('\r\n').split(": ",1)
            key = key.upper().replace('-','_')
            env[key] = value
        else:
            return envTemplates.Error400Env("wrong headers") # evil

    if 'COOKIE' in env.keys():
        env['HTTP_COOKIE'] = env['COOKIE']

    content = ''
    cLen = int(env['CONTENT_LENGTH'])
    if cLen > MaxFileSize:
        return envTemplates.Error400Env("Request size too big")
    if cLen > 0:
        while len(content) < cLen:
            content += conn.recv(BuffSize)
    #print "%s%s" % (repr(reqRaw), repr(content),) # for printing request
    env['wsgi.input'] = StringIO.StringIO(content)
    return env

# Parse the command line arguments
# return the argument
def parse_sys_arg():
    parser = argparse.ArgumentParser(description='Run a WSGI server.')
    parser.add_argument('-a', '-A', '--app', default = 'default',\
                        metavar = 'App', choices = AppChoices,\
                        help='The WSGI app to run')
    parser.add_argument('-p', '--port', default=random.randint(8000,8009),\
                        type=int, metavar='Port',help='Port number to run')
    return parser.parse_args()

if __name__ == '__main__':
    main()
