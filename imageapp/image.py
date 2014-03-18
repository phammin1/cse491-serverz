# image handling API

from mimetypes import guess_type # for mapping file extension to mimetype

images = {}
imageName = {}

# Add an image using data and name of image file
def add_image(data, fileName = "abc.png"):
    if images:
        image_num = max(images.keys()) + 1
    else:
        image_num = 0
        
    images[image_num] = data
    imageName[image_num] = fileName
    return image_num

# get image and its type
def get_image(num):
    return images[num], guess_type(imageName[num])[0]

# get image and its type
def get_latest_image():
    image_num = max(images.keys())
    return get_image(image_num)
