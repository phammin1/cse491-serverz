#!/usr/bin/env python
# Minh Pham
# CSE 491

from app import make_app # for making an app

# Quixote import
import quixote
from quixote.demo.altdemo import create_publisher

# App import
import imageapp
from quotes.apps import QuotesApp
from chat.apps import ChatApp

# Currently implement app for deploy
AppChoices = ['imageapp', 'i', 'altdemo', 'a', 'quotes', 'q',\
                  'chat', 'c', 'default']

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
