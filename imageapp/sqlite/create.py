# create the database 'images.sqlite' and create a table 'image_store' inside
# of it.

import sqlite3

db = sqlite3.connect('images.sqlite')
db.execute('CREATE TABLE image_store (i INTEGER PRIMARY KEY, image BLOB, description TEXT, file_name TEXT)');
db.commit()
db.close()

# here, the database is images.sqlite; it contains one table, image_store;
# 'i' is a column that provides a unique key for retrieval (and is optimized
#   for that; 'image_store' is another column that contains large binary
#   objects (blobs).
