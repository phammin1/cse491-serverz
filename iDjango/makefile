all: run

run:
	python ../server.py -a d

db: 
	python manage.py syncdb

cdb: clear db

clear:
	rm -rf db.sqlite3
	rm -rf media/*