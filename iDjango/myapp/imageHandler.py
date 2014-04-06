# image handling API

from mimetypes import guess_type # for mapping file extension to mimetype
import os # for getting absolute path
import json # for AJAX response in json
from models import MyImage, MyComment # for storing in database
from time import time # for time control to used with ajax 
from datetime import datetime # for making time from timestamp
from django.utils.timezone import utc # to get rid of warning error for tzinfo

# Time string formatter to make time look nice
TimeFormatter = "%b %d at %H:%M"

# store image as list
# an image dictionary is expected to have the following
# data, filename, description
# best to used get default image
images = []

# get image from a form with query
# mostly do error checking
def get_image_number_from_form(aForm):
    if 'i' not in aForm.keys():
        aQuery = ""
    else:
        aQuery = aForm['i']
        
    if aQuery == "0" or aQuery == "":
        imgNum = get_latest_num()
    else:
        try:
            imgNum = int(aQuery)
        except ValueError:
            print "Query is not a number: '", aQuery,"'"
            imgNum = 1
    if imgNum < 1:
        # check for evil input
        print "Something evil happen: Image number less than 1"
        imgNum = 1
    if imgNum > get_latest_num():
        # check if image number index is too big
        print "Something stupid happen: Image number too big"
        imgNum = get_latest_num()
    
    return imgNum

# get image from a form with query
# return image and its type
def get_image_from_form(aForm):
    imgNum = get_image_number_from_form(aForm)
    img = MyImage.sql.get(pk=imgNum)
    return img.image, guess_type(img.name)[0]

# get image thumbnail from a form with query
def get_thumbnail_from_form(aForm):
    imgNum = get_image_number_from_form(aForm)
    img = MyImage.sql.get(pk=imgNum)
    return img.thumbnail, "image/png"

# get last image number:
def get_latest_num():
    return MyImage.sql.count()

# add image from a form
def add_image_from_form(aForm):
    the_file = aForm['image']
    fileName = str(the_file)
    description = aForm['description']
    print 'Adding image with name:', fileName

    # Create an image to add to "database"
    img = MyImage(name=fileName, description=description, image=the_file)
    img.save()
    
# Search for image using a form
def search_image(aForm):
    retList = MyImage.sql.meta().filter(
        name__contains=aForm["file"]).filter(
        description__contains=aForm["description"])
        
    if len(retList) == 0:
        return {"status" : "fail"}
    else:
        return {"results" : retList}

# Get a detail dict used to generate list of image
def get_detail_dict():
    images = MyImage.sql.all().values('id', 'name', 'description')
    return {"results": images}

# Get meta data of an image from the usual form
# form must have i field which is the image number
# return the metadata in dictionary format
def get_metadata(aForm):
    imgNum = get_image_number_from_form(aForm)
    image = MyImage.sql.values('id', 'name', 'description').get(pk=imgNum)
    image["time"] = time()
    image["commentList"] = MyComment.objects.values('user', 'comment', 'datetime').filter(imageId=imgNum)
    return image

# Add comment to the image using form
def add_comment(aForm):
    i = check_imageId(aForm["imageId"])
    
    comment = MyComment(comment=aForm["comment"], user=aForm["user"], imageId=i)
    comment.save()
    return "success"

# Sanitize the image id
# return -1 if wrong image id
def check_imageId(i):
    if i < 0 or i > get_latest_num():
        return -1
    if i == 0:
        return get_latest_num()

    return i

# Return a list of comment based on the form time
# used to get comments async
def get_comment_list(aForm):
    try:
        refDate = datetime.fromtimestamp(aForm["time"], tz=utc)
    except ValueError:
        print "Supreme evil: date time error in ajax comment"
        return "fail", "text"

    comments = MyComment.objects.filter(imageId=aForm["imageId"]
                                        ).filter(datetime__gt=refDate)

    results = [ob.as_json() for ob in comments]
    retDict = {"results" : results, "time" : time()}
    return json.dumps(retDict), "application/json"



