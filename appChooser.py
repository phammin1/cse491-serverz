#!/usr/bin/env python
# Minh Pham
# CSE 491

from app import make_app # for making a simple app

# Quixote import
import quixote
from quixote.demo.altdemo import create_publisher

# App import
import imageapp
from quotes.apps import QuotesApp
from chat.apps import ChatApp

# For django path environment
import os
import sys

# Currently implement app for deploy
AppChoices = ['imageapp', 'i', 'altdemo', 'a', 'quotes', 'q',\
                  'chat', 'c', 'django', 'cookie', 'ck', 'd', 'default']

# Django app directory
DjangoDir = "iDjango"

# Django setting file
DjangoSettingFile = "core.settings"

# Choose an app depend on path info in env
def choose_app(appStr):
    if appStr == 'imageapp' or appStr == 'i':
        return make_image_app()
    elif appStr == 'altdemo' or appStr == 'a':
        return make_altdemo_app()
    elif appStr == 'quotes' or appStr == 'q':
        return QuotesApp('quotes/quotes.txt', 'quotes/html')
    elif appStr == 'chat' or appStr == 'c':
        return ChatApp('chat/html')
    elif appStr == 'django' or appStr == 'd':
        return make_django_app()
    elif appStr == 'cookie' or appStr == 'ck':
        import cookieapp
        return cookieapp.wsgi_app
    else:
        # Default value
        print 'Using default app...'
        return make_app()
    
# make image app
def make_image_app():
    imageapp.setup()
    imageapp.create_publisher()
    return quixote.get_wsgi_app()

def make_altdemo_app():
    create_publisher()
    return quixote.get_wsgi_app()

def make_django_app():
    # Credit to Brian Jurgess
    settingDir = DjangoDir + '.' + DjangoSettingFile
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settingDir)
    from django.core.wsgi import get_wsgi_application
    sys.path.append(os.path.join(os.path.dirname(__file__), DjangoDir))

    return get_wsgi_application()
    
