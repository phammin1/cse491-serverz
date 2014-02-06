#!/usr/bin/env python
# Minh Pham
# CSE 491

import random
import socket
import time
from urlparse import urlparse, parse_qs  # credit to Jason Lefler code
import signal # to control execution time
import cgi # to parse post data
import jinja2 # for html template
import StringIO # for string buffer

# jinja file path
jinjaTemplateDir = './templates'

# buffer size for conn.recv
buffSize = 10

def main():
    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    #port = 2906
    s.bind((host, port))        # Bind to the port
    
    jLoader = jinja2.FileSystemLoader(jinjaTemplateDir)
    jEnv = jinja2.Environment(loader=jLoader)
    
    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        conn, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(conn, jEnv)

# control execution time
def signal_handler(signum, frame):
    raise Exception("Timed out!")

def handle_connection(conn, jEnv):
    global reqData # to fix issue with reqData assignment inside function
    reqData = ""
    # signal is used to control execution time
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, .3, .3) # .3 second

    try:
        while True:
            reqData += conn.recv(buffSize)
    except Exception, msg:
        signal.alarm(0) # turn off signal
    signal.alarm(0) # just to make sure

    page = getPage(reqData)
    formFS = createFS(reqData)
    
    try:
        serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
        serverResponse += jEnv.get_template(page).render(formFS)
    except jinja2.exceptions.TemplateNotFound:
        serverResponse = error404(jEnv, reqData)
 
    conn.send(serverResponse)
    conn.close()

# Get page name from request data
def getPage(reqData):
    path = urlparse(reqData.split()[1])[2] # credit to Jason Lefler
    path = path.lstrip('/')
    # index page
    if path == '':
        path = 'index'
    path += '.html'

    return path

# initialize field storage object based on request data
# specialized for post method, but also work with GET
def createFS(reqData):
    buf = StringIO.StringIO(reqData)
    line = buf.readline()
    env = {'REQUEST_METHOD' : line.split()[0]}

    # create query string to work with GET method
    uri = line.split()[1]
    queryString = ''
    if "?" in uri:
        queryString = uri.split('?',1)[-1]
    env['QUERY_STRING'] = queryString

    headers = {}

    while True:
        line = buf.readline()
        if line == '\r\n':
            # empty line = end of header section
            break

        lineList = line.strip('\r\n').split(':')
        headers[lineList[0].lower()] = lineList[1] # credit to Ben Taylor
    # to make fieldstorage work with get
    if not 'content-type' in headers:
        headers['content-type'] = 'application/x-www-form-urlencoded'
            
    # credit to Maxwell Brown and Xavier Durand-Hollis
    formFS = cgi.FieldStorage(fp = buf, headers=headers, environ=env)
    return formFS

def error404(jEnv, reqData):
    serverResponse = 'HTTP/1.0 404 Not Found\r\n'
    serverResponse += 'Content-type: text/html\r\n\r\n'
    serverResponse += jEnv.get_template('notFound.html').render()
    
    return serverResponse

if __name__ == '__main__':
    main()
