#!/usr/bin/env python
# Minh Pham
# CSE 491

import random
import socket
import time

def main():

    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
    #port = random.randint(8000, 9999)
    port = 2907
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
    path = reqData.split('\n')[0].split(' ')[1]
    if path == '/':
        serverResponse = indexP(conn, reqData)
    elif path == '/content':
        serverResponse = contentP(conn, reqData)
    elif path == '/file':
        serverResponse = fileP(conn, reqData)
    elif path == '/image':
        serverResponse = imageP(conn, reqData)
    else :
        serverResponse = error404(conn, reqData)

    return serverResponse
    
def indexP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Hello</h1>" + \
                   '<a href="/content">Content</a><br></br>' + \
                   '<a href="/file">File</a><br></br>' + \
                   '<a href="/image">Image</a><br></br>' + \
                   "This is Minh\'s Web server." 
    return serverResponse
    
def contentP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                   "<h1>Content</h1>This is Minh\'s Web server."
    return serverResponse
    
def fileP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                   "<h1>File</h1>This is Minh\'s Web server."
    return serverResponse
    
def imageP(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Image</h1>This is Minh\'s Web server."
    return serverResponse
    
def error404(conn, reqData):
    serverResponse = 'HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>Not Found</h1>This is Minh\'s Web server."
    return serverResponse
    
def handle_post(conn, reqData):
    serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + \
                     "<h1>POST method</h1>This is Minh\'s Web server."
    return serverResponse
    
if __name__ == '__main__':
    main()
