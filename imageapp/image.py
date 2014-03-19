# image handling API

from mimetypes import guess_type # for mapping file extension to mimetype

images = []
# store image as dictionary
# an image dictionary is expected to have the following
# data, filename, description
# best to used get default image

# Add an image using data and name of image file
# param img an image dictionary
def add_image(img):        
    images.append(img)
    return len(images)

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

# get last image number:
def get_latest_num():
    return len(images)-1

# get default image (default is empty)
def create_image_dict(data = "", fileName = "default.png", description = "No description available"):
    img = {"data" : data}
    img["file_name"] = fileName
    img["description"] = description
    img["commentList"] = []
    return img

# create image from a form
def add_image_from_form(aForm):
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
    return imgDict
