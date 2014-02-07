# Minh Pham
# CSE 491

from wsgiref.util import setup_testing_defaults
import cgi
import jinja2
from werkzeug.wrappers import Response

# jinja file path
JinjaTemplateDir = './templates'

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    setup_testing_defaults(environ)

    jEnv = jinja2.Environment(\
        loader=jinja2.FileSystemLoader(JinjaTemplateDir),\
            autoescape=True)

    reqPage = getPage(environ['PATH_INFO'])
    reqFS = cgi.FieldStorage(fp = environ['wsgi.input'],environ=environ)

    try:
        tmp = jEnv.get_template(reqPage).render(reqFS)
        ret = Response(tmp, mimetype ='text/html')
    except jinja2.exceptions.TemplateNotFound:
        #raise NotFound()
        ret = error404(jEnv)

    return ret(environ, start_response)

def error404(jEnv):
    tmp = jEnv.get_template('notFound.html').render()
    ret = Response(tmp, mimetype ='text/html')
    ret.status = '404 Not Found'
    return ret

def make_app():
    return simple_app

# Get page name from path
def getPage(path):
    path = path.lstrip('/')
    if path == '':
        path = 'index'
    if not '.' in path:
        path += '.html'

    return path
