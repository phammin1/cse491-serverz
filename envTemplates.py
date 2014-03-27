# Singleton module to make some constant environ
import StringIO
from sys import stderr

# Credit to Ben Taylor for the specifics
def DefaultEnv(host='fake', port =0):
    return {\
    'REQUEST_METHOD' : 'GET',\
        'QUERY_STRING' : '',\
        'PATH_INFO': '/',\
        'CONTENT_TYPE' :'application/x-www-form-urlencoded',\
        'CONTENT_LENGTH' : '0',\
        'SCRIPT_NAME': '',\
        'SERVER_NAME' : host,\
        'SERVER_PORT' : str(port),\
        'wsgi.version' : (1,0),\
        'wsgi.input' : StringIO.StringIO(''),\
        'wsgi.errors' : stderr,\
        'wsgi.multithread' : False,\
        'wsgi.multiprocess' : False,\
        'wsgi.run_once' : False,\
        'wsgi.url_scheme' : 'http'
    }

Error404Env = {\
    'REQUEST_METHOD' : 'GET',\
        'QUERY_STRING' : '',\
        'PATH_INFO': '/fakeabcsz',\
        'CONTENT_TYPE' :'application/x-www-form-urlencoded',\
        'CONTENT_LENGTH' : '0',\
        'SCRIPT_NAME': '',\
        'SERVER_NAME' : 'arctic.cse.msu.edu',\
        'SERVER_PORT' : 'abc',\
        'wsgi.version' : (1,0),\
        'wsgi.input' : StringIO.StringIO(''),\
        'wsgi.errors' : stderr,\
        'wsgi.multithread' : False,\
        'wsgi.multiprocess' : False,\
        'wsgi.run_once' : False,\
        'wsgi.url_scheme' : 'http'
    }

# for bad request type
def Error400Env(msg = "Evil request"):
    return {\
    'REQUEST_METHOD' : 'GET',\
        'QUERY_STRING' : 'msg=' + msg ,\
        'PATH_INFO': '/badRequest',\
        'CONTENT_TYPE' :'application/x-www-form-urlencoded',\
        'CONTENT_LENGTH' : '0',\
        'SCRIPT_NAME': '',\
        'SERVER_NAME' : 'arctic.cse.msu.edu',\
        'SERVER_PORT' : 'abc',\
        'wsgi.version' : (1,0),\
        'wsgi.input' : StringIO.StringIO(''),\
        'wsgi.errors' : stderr,\
        'wsgi.multithread' : False,\
        'wsgi.multiprocess' : False,\
        'wsgi.run_once' : False,\
        'wsgi.url_scheme' : 'http'
    }
