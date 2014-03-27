# Minh Pham
# CSE 491

import cgi # for fieldStorage - parsing data
import jinja2 # for template
from werkzeug.wrappers import Response # for making wrapper class
from mimetypes import guess_type # for mapping file extension to mimetype

# jinja file path
JinjaTemplateDir = './templates'

# Other type of resources (.ico, .jpg, ...)
ResDir = './resources'

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    if environ['PATH_INFO'] == '/file':
        environ['PATH_INFO'] = '/file.txt'
    elif environ['PATH_INFO'] == '/image':
        environ['PATH_INFO'] = '/image.jpg'
        
    if '.' in environ['PATH_INFO'] and '.html' not in environ['PATH_INFO']:
        # request for something other than html page
        ret = handle_resources(environ)
    else:
        # html request
        ret = handle_html(environ)

    return ret(environ, start_response)

# return a 404 response
def error404():
    jEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(JinjaTemplateDir))
    tmp = jEnv.get_template('notFound.html').render()
    ret = Response(tmp, mimetype ='text/html')
    ret.status = '404 Not Found'
    return ret
    
# Handle all html page request
def handle_html(environ):
    jEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(JinjaTemplateDir))

    path = environ['PATH_INFO']
    if path == '/':
        path = '/index'
    if not '.' in path:
        path += '.html'

    reqFS = cgi.FieldStorage(fp = environ['wsgi.input'],environ=environ)

    try:
        tmp = jEnv.get_template(path).render(reqFS)
        ret = Response(tmp, mimetype ='text/html')
    except jinja2.exceptions.TemplateNotFound:
        return error404()

    if path == '/badRequest.html':
        ret.status = '400 Bad Request'

    return ret

# Handle resources (.txt, .jpg, .ico,...) request
def handle_resources(environ):
    fileDir = ResDir + environ['PATH_INFO']
    try:
        fp = open(fileDir, 'rb')
    except IOError:
        # File not found
        return error404()

    data = fp.read()
    fp.close()
    return Response(data, mimetype = guess_type(fileDir)[0])

def make_app():
    return simple_app
