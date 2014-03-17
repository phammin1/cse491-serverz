#!/usr/bin/env python
# Minh Pham
# CSE 491

import random, socket, time
from urlparse import urlparse  # credit to Jason Lefler code
import signal # to control execution time
import StringIO # for string buffer
from app import make_app # for making an app
from wsgiref.validate import validator # validating server side
import sys, getopt # for command line argument
import envTemplates # for some default environment

# Quixote import
import quixote
from quixote.demo.altdemo import create_publisher

# Other import
import imageapp

# make image app
def make_image_app():
    imageapp.setup()
    imageapp.create_publisher()
    return quixote.get_wsgi_app()

def make_altdemo_app():
    create_publisher()
    return quixote.get_wsgi_app()

# buffer size for conn.recv
BuffSize = 128

# timeout for conn.recv (in seconds)
ConnTimeout = .1

def main(socketModule = None):
    # choose app based on system argument
    appStr = parse_sys_arg()
    myApp = choose_app(appStr)
    
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
        handle_connection(conn, host, port, myApp)

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
            
    reqData = getData(conn)
    reqEnv = createEnv(reqData, defaultEnv)
    #myApp = validator(anApp)
    myApp = anApp
    resPage = myApp(reqEnv, start_response) # normal server
    
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
        return envTemplates.Error404Env # evil empty request
    
    buf = StringIO.StringIO(reqData)
    line = buf.readline()

    # some default value to avoid code breaking
    env = defaultEnv.copy()
    env['REQUEST_METHOD'] = line.split()[0]
    
    try:
        uri = line.split()[1]
    except IndexError:
        return envTemplates.Error404Env # more evil request    
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
            return envTemplates.Error404Env

    if 'COOKIE' in env.keys():
        env['HTTP_COOKIE'] = env['COOKIE']
    env['wsgi.input'] = buf
    return env

# Choose an app depend on path info in env
# from http://www.tutorialspoint.com/python/python_command_line_arguments.htm
def choose_app(appStr):
    if appStr == 'imageapp':
        return make_image_app()
    elif appStr == 'altdemo':
        return make_altdemo_app()
    else:
        # Default value
        print 'Using default app...'
        return make_app()

def parse_sys_arg():
   appStr = '' # default to avoid breaking

   # parsing the sys arguments using getopt
   try:
       opts, args = getopt.getopt(sys.argv[1:], "a:a", ["app="])
   except getopt.GetoptError:
       print 'Error 2: Parsing of command line argument error'
       print_help()
       return 'default'
   
   for opt, arg in opts:
      if opt == '-h': # help option
         print_help()
         sys.exit()
      if opt in ('-a', '--app'): # app option
         appStr = arg 
   
   print 'App option: ', appStr, '...'

   return appStr

def print_help():
    print 'usage: python server.py -a <app>'

if __name__ == '__main__':
    main()
