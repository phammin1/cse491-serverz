# retrieve an image from the database.

import sqlite3
import sys

# connect to database
db = sqlite3.connect('images.sqlite')

# configure to retrieve bytes, not text
db.text_factory = bytes

# get a query handle (or "cursor")
c = db.cursor()

# select all of the images
c.execute('SELECT i, image FROM image_store ORDER BY i DESC LIMIT 1')
#          ^      ^             ^           ^
#          ^      ^             ^           ^----- details of ordering/limits
#          ^      ^             ^
#          ^      ^             ^--- table from which you want to extract
#          ^      ^
#          ^      ^---- choose the columns that you want to extract
#          ^
#          ^----- pick zero or more rows from the database


# grab the first result (this will fail if no results!)
i, image = c.fetchone()

# write 'image' data out to sys.argv[1]
print 'writing image', i
open(sys.argv[1], 'w').write(image)

