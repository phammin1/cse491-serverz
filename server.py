#!/usr/bin/env python
# Minh Pham
# CSE 491

import random
import socket
import time
from urlparse import urlparse, parse_qs  # credit to Jason Lefler code


def main():

    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    #port = 2906
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

def handle_connection(conn):
    reqData = conn.recv(1000)
    reqMethod = reqData.split('\n')[0].split(' ')[0]

    if reqMethod == 'GET':
        serverResponse = handle_get(conn,reqData)
    elif reqMethod == "POST":
        serverResponse = handle_post(conn,reqData)
    else:
        serverResponse = error404(conn, reqData)

    conn.send(serverResponse)
    conn.close()

def handle_get(conn,reqData):
    path = urlparse(reqData.split()[1])[2] # credit to Jason Lefler

    if path == '/':
        serverResponse = indexP(conn, reqData)
    elif path == '/content':
        serverResponse = contentP(conn, reqData)
    elif path == '/file':
        serverResponse = fileP(conn, reqData)
    elif path == '/image':
        serverResponse = imageP(conn, reqData)
    elif path == '/form':
        serverResponse = formP(conn, reqData)
    elif path == '/submit':
        serverResponse = submitP(conn, reqData)
    elif path == '/formPost':
        serverResponse = formPostP(conn, reqData)
    else :
        serverResponse = error404(conn, reqData)

    return serverResponse
    
def indexP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Hello</h1>" + \
                   '<a href="/content">Content</a><br></br>' + \
                   '<a href="/file">File</a><br></br>' + \
                   '<a href="/image">Image</a><br></br>' + \
                   '<a href="/form">Form</a><br></br>' +\
                   '<a href="/formPost">Form (Post)</a><br></br>' +\
                   "This is Minh\'s Web server." 
    return serverResponse
    
def contentP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                   "<h1>Content</h1>" +\
                   '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."
    return serverResponse
    
def fileP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                   "<h1>File</h1>" +\
                   '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."
    return serverResponse
    
def imageP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Image</h1>" +\
                     '<a href="/">Home</a><br></br>' +\
                     "This is Minh\'s Web server."
    return serverResponse

def formP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Form</h1>" + \
                     "<form action='/submit' method='GET'>" +\
                     "<input type='text' name='firstname'><br></br>" +\
                     "<input type='text' name='lastname'><br></br>" +\
                     "<input type='submit' name='submit'><br></br>" +\
                     "</form>" +\
                     '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."
    return serverResponse

def formPostP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Form Post</h1>" + \
                     "<form action='/submit' method='POST'>" +\
                     "<input type='text' name='firstname'><br></br>" +\
                     "<input type='text' name='lastname'><br></br>" +\
                     "<input type='submit' name='submit'><br></br>" +\
                     "</form>" +\
                     '<a href="/">Home</a><br></br>' +\
                   "This is Minh\'s Web server."
    return serverResponse

def submitP(conn, reqData):
    formData = parse_qs(urlparse(reqData.split()[1])[4])# credit to Jason Lefler
    try:
        firstName = formData['firstname'][0]
    except KeyError:
        firstName = 'No'
    try:
        lastName = formData['lastname'][0]
    except KeyError:
        lastName = 'Name'
        
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Hello %s %s</h1>" %(firstName,lastName,) +\
                     '<a href="/">Home</a><br></br>' +\
                     "This is Minh\'s Web server."
    return serverResponse

def error404(conn, reqData):
    serverResponse = 'HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n' + \
                      '<a href="/">Home</a><br></br>' +\
                     "<h1>Not Found</h1>This is Minh\'s Web server."
    return serverResponse

def handle_post(conn, reqData):
    path = urlparse(reqData.split()[1])[2] # credit to Jason Lefler
    if path == '/':
        serverResponse = postP(conn, reqData)
    elif path == '/submit':
        serverResponse = submitPostP(conn, reqData)
    else:
        serverResponse = error404(conn, reqData)
    return serverResponse

def postP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>POST method</h1>" +\
                     '<a href="/">Home</a><br></br>' +\
                     "This is Minh\'s Web server."
    return serverResponse

def submitPostP(conn, reqData):
    formData = parse_qs(reqData.split('\n')[-1])# credit to Jason Lefler
    #print formData
    try:
        firstName = formData['firstname'][0]
    except KeyError:
        firstName = 'No'
    try:
        lastName = formData['lastname'][0]
    except KeyError:
        lastName = 'Name'
        
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>(Post) Hello %s %s</h1>" %(firstName,lastName,) +\
                     '<a href="/">Home</a><br></br>' +\
                     "This is Minh\'s Web server."
    return serverResponse

if __name__ == '__main__':
    main()
