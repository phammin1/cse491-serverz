# image handling API

from mimetypes import guess_type # for mapping file extension to mimetype
from time import time, strftime # for time control of the comment
from PIL import ImageFile, Image # for generating thumbnail
import os # for getting absolute path
from StringIO import StringIO # for buffer
from sqlite import query

# Time string formatter to make time look nice
TimeFormatter = "%b %d at %H:%M"

# Default no preview thumbnail (default format is png)
DefaultThumbnail = "no_preview.png"

# Default Thumbnail size
ThumbnailSize = 70, 70

# store image as list
# an image dictionary is expected to have the following
# data, filename, description
# best to used get default image
images = []

# Add an image using data and name of image file
# param img an image dictionary
def add_image(img):        
    images.append(img)
    query.insert(img)
    return len(images)

# Load image from dictionary from database
# Do not save to databse
def load_image_from_form(aDict):
    img = create_image_dict(data = aDict["data"], fileName = aDict["file_name"],
                                       description = aDict["description"])
    images.append(img)
    
# get image and its type
def get_image(num):
    img = images[num]
    return img["data"], guess_type(img["file_name"])[0]

# get image from a form with query
# mostly do error checking
def get_image_number_from_form(aForm):
    if 'i' not in aForm.keys():
        aQuery = ""
    else:
        aQuery = aForm['i']
        
    if aQuery == "latest" or aQuery == "":
        imgNum = get_latest_num()
    else:
        try:
            imgNum = int(aQuery)
        except ValueError:
            print "Query is not a number: '", aQuery,"'"
            imgNum = 0
    if imgNum < 0:
        # check for evil input
        print "Something evil happen: Image number negative"
        imgNum = 0
    if imgNum > get_latest_num():
        # check if image number index is too big
        print "Something stupid happen: Image number too big"
        imgNum = get_latest_num()
    
    return imgNum

# get image from a form with query
# mostly do error checking
def get_image_from_form(aForm):
    imgNum = get_image_number_from_form(aForm)
    return get_image(imgNum)

# get image thumbnail from a form with query
def get_thumbnail_from_form(aForm):
    imgNum = get_image_number_from_form(aForm)
    return images[imgNum]["thumbnail"], "image/png"

# get last image number:
def get_latest_num():
    return len(images)-1

# get default image (default is empty)
def create_image_dict(data = "", fileName = "default.png", description = "No description available"):
    img = {"data" : data}
    img["file_name"] = fileName
    img["description"] = description
    img["commentList"] = []
    img["thumbnail"] = generate_thumbnail(data)
    
    return img

# create image from a form
def add_image_from_form(aForm):
    if 'file' not in aForm.keys() or 'description' not in aForm.keys():
        print 'Evil arise: Cannot add image from improper form'
        return
    the_file = aForm['file']
    description = aForm['description']
    print 'Adding image with name:', the_file.base_filename
    data = the_file.read(int(1e9))

    # Create an image dictionary to add to "database"
    img = create_image_dict(data=data,\
         description = description,  fileName=the_file.base_filename)
    add_image(img)
    
# Search for image using a form
def search_image(aForm):
    fileSet = set(search_image_dict(aForm["file"], "file_name"))
    desSet = set(search_image_dict(aForm["description"], "description"))

    return create_search_result(fileSet.intersection(desSet))

# Search for image using aStr
# return a list of index of image with the field contains the string
def search_image_dict(aStr, aField):
    i = 0
    resultInx = []
    for img in images:
        if aStr in img[aField]:
            resultInx.append(i)
        i += 1
    return resultInx

# Create the search result dictionary from the result list
# format of the result dict:
# status : fail or success
# index: list of found index
# file_name: file name of those images
# description: description of images
def create_search_result(resultSet):
    if len(resultSet) == 0:
        return {"status" : "fail"}
    else:
        resultDict = {"status" : "success"}
        resultDict["results"] = []
        for i in resultSet:
            result = {"index":i}
            result["file_name"] = images[i]["file_name"]
            result["description"] = images[i]["description"]
            resultDict["results"].append(result)
            
    return resultDict

# get information about an image from the form
# pre form should have at least two field: q and f
# q is the image number
# f is the field request
def get_detail(aForm):
    imgNum = get_image_number_from_form(aForm)
    if 'f' not in aForm.keys():
        print "Evil request. No field in get_detail"
        return ""
    else:
        field = aForm['f']
    if field not in images[0].keys():
        print "I skew up big time. Key invalid: ", field
        return ""
    else:
        return images[imgNum][field]

# Get a detail dict used to generate list of image
def get_detail_dict():
    i = 0
    imgList = []
    for img in images:
	imgDict = {"index" : i}
	imgDict["file_name"] = img["file_name"]
	imgDict["description"] = img["description"]
	imgList.append(imgDict)
	i += 1
    return {"results": imgList}

# Get meta data of an image from the usual form
# form must have i field which is the image number
# return the metadata in dictionary format
def get_metadata(aForm):
    imgNum = get_image_number_from_form(aForm)
    img = images[imgNum]
    imgDict = {}
    imgDict["index"] = imgNum
    imgDict["file_name"] = img["file_name"]
    imgDict["description"] = img["description"]
    imgDict["commentList"] = img["commentList"]
    imgDict["time"] = time()
    return imgDict

# Add comment to the image using form
# Doing AJAX
def add_comment(aForm):
    imgNum = get_image_number_from_form(aForm)
    img = images[imgNum]
    result = {"status": "fail"}
    if 'user' in aForm.keys() and 'comment' in aForm.keys():
        result["time"] = time()
        # check if there is an user or comment to add
        if aForm["user"] != "" and aForm["comment"] != "":
            comment = {"user": aForm["user"]}
            comment["comment"] = aForm["comment"].strip()
            comment["time"] = time()
            img["commentList"].append(comment)
            comment["time"] = result["time"]
            comment["timeHumanReadable"] = strftime(TimeFormatter)

        formTime = 0
        if "time" in aForm.keys():
            # check timestamp
            try:
                formTime = (float) (aForm["time"].strip())
            except ValueError:
                print "Time is not a number: '", aForm["time"],"'"
                return result
        else:
            # No timestamp, probably debugging
            return result
        result["status"] = "success"
        
        # find all comment that is after the timestamp
        i = 0
        for cmt in img["commentList"]:
            if cmt["time"] > formTime:
                break
            i += 1
        result["result"] = img["commentList"][i:]
    else:
        print 'Evil or stupid: Wrong form keys in add_comment'
    return result

# Generate thumbnail using data
# return: a file pointer like object
def generate_thumbnail(data):
    # read data into PIL image
    p = ImageFile.Parser()
    img = None
    try:
        p.feed(data)
        img = p.close()
    except Exception, msg:
        print "Can't generate thumbnail:", msg

    # if cannot read the image file using PIL
    if img == None:
        # generate a default thumbnail
        dirname = os.path.join(os.path.dirname(__file__),"")
        thumbnail_path = os.path.join(dirname, DefaultThumbnail)
        return open(thumbnail_path, 'rb').read()
    else:
        # generate an actual thumbnail
        fp = StringIO()
        img.thumbnail(ThumbnailSize, Image.ANTIALIAS)
        img.save(fp, format="PNG")
        fp.seek(0)
        return fp.read()
