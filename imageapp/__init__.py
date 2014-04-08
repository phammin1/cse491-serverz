# __init__.py is the top level file in a Python package.

from quixote.publish import Publisher

# this imports the class RootDirectory from the file 'root.py'
from .root import RootDirectory
from . import html, image
from sqlite import query

def create_publisher():
     p = Publisher(RootDirectory(), display_exceptions='plain')
     p.is_thread_safe = True
     return p
 
def setup():                            # stuff that should be run once.
    html.init_templates()
    #add_default_image()
    loadDb()

def teardown():                         # stuff that should be run once.
    pass

# Add some default images
def add_default_image():
    some_data = open('imageapp/favicon.ico', 'rb').read()
    img = image.create_image_dict(data = some_data, fileName = "fav.ico",\
                                       description = "Favorite icon")
    image.add_image(img)
    commentForm = {'i': 0, 'user': 'Minh', 'comment': 'Small file for testing'}
    image.add_comment(commentForm)
    
    some_data = open('imageapp/dice.png', 'rb').read()
    img = image.create_image_dict(data = some_data, fileName = "dice.png",\
                                       description = "Four colorful dices")
    image.add_image(img)
    commentForm = {'i': 1, 'user': 'Minh', 'comment': 'First comment ever'}
    image.add_comment(commentForm)

    some_data = open('imageapp/tux.png', 'rb').read()
    img = image.create_image_dict(data = some_data, fileName = "tux.png",\
                                       description = "Tux the Linux penguin")
    image.add_image(img)
    commentForm = {'i': 2, 'user': 'Minh', 'comment': 'Have you play SuperTux?'}
    image.add_comment(commentForm)

# Load data from database
def loadDb():
     imageDictList = query.loadAll()
     for imgDict in imageDictList:
          image.load_image_from_form(imgDict)
