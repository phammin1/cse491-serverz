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
    port = 2906
    s.bind((host, port))        # Bind to the port

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.    
        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(c)

def handle_connection(c):
    reqData = c.recv(1000)
    reqMethod = reqData.split('\n')[0].split(' ')[0]

    if reqMethod == 'GET':
        handle_get(c,reqData)
    elif reqMethod == "POST":
        handle_post(c,reqData)
    else:
        error404(c)
        
    c.close()

def handle_get(c,reqData):
    path = reqData.split('\n')[0].split(' ')[1]
    if path == '/':
        handle_default(c)
    elif path == '/content':
        handle_content(c)
    elif path == '/file':
        handle_file(c)
    elif path == '/image':
        handle_image(c)
    else :
        error404(c)
    
def handle_default(c):
    c.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>Hello</h1>")
    c.send('<a href="content">Content</a><br></br>')
    c.send('<a href="file">File</a><br></br>')
    c.send('<a href="image">Image</a><br></br>')
    c.send("This is Minh\'s Web server.")

def handle_content(c):
    c.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>Content</h1>This is Minh\'s Web server.")

def handle_file(c):
    c.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>File</h1>This is Minh\'s Web server.")

def handle_image(c):
    c.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>Image</h1>This is Minh\'s Web server.")

def error404(c):
    c.send('HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>Not Found</h1>This is Minh\'s Web server.")

def handle_post(c,reqData):
    c.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    c.send("<h1>POST method</h1>This is Minh\'s Web server.")    
    
if __name__ == '__main__':
    main()
