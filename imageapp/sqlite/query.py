# insert an image into the database.

import sqlite3

# Sqlite database file
DbFile = "imageapp/sqlite/images.sqlite"

# Insert image to the database
def insert(img):
    # connect to the already existing database
    db = sqlite3.connect(DbFile)
    # configure to allow binary insertions
    db.text_factory = bytes
    c= db.cursor()
    # insert!
    c.execute('INSERT INTO image_store (image, description, file_name) VALUES (?,?,?)', (img["data"],img["description"], img["file_name"]))
    db.commit()
    db.close()

# Load everything from database
def loadAll():
    # connect to the already existing database
    db = sqlite3.connect(DbFile)
    # configure to allow binary insertions
    db.text_factory = bytes
    c = db.cursor()
    # get all data
    imageList = []
    for row in c.execute('SELECT * FROM image_store'):
        imgForm = {}
        imgForm["data"] = row[1]
        imgForm["description"] = row[2]
        imgForm["file_name"] = row[3]
        imageList.append(imgForm)
        
    db.commit()
    db.close()

    return imageList
