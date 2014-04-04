from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import imageHandler
import json # for AJAX

def index(request):
    return render(request,'index.html')

def upload(request):
    return render(request,'upload.html')

def upload_receive(request):
    if request.method == 'POST': # If the form has been submitted...
        form = request.POST # A form bound to the POST data
        if "file" in request.FILES:
            form["file"] = request.FILES["file"]
        imageHandler.add_image_from_form(form)
    else:
        print "Evil user: GET in upload_receive"
    return HttpResponseRedirect('/')

def image_raw(request):
    img, contentType = imageHandler.get_image_from_form(request.GET)
    return HttpResponse(img, content_type=contentType)
    
def image(request, imgNum):
    imgDict = imageHandler.get_metadata({"i" : imgNum})
    return render(request,'image.html', dictionary=imgDict)

def image_latest(request):
    imgNum = imageHandler.get_latest_num()
    return HttpResponseRedirect('/image/' + str(imgNum))

def add_image(request):
    imageHandler.add_default_image()
    return HttpResponseRedirect('/')

def image_list(request):
    imgDict = imageHandler.get_detail_dict()
    return render(request, 'image_list.html', dictionary=imgDict)

def image_thumbnail(request):
    img, contentType = imageHandler.get_thumbnail_from_form(request.GET)
    return HttpResponse(img, content_type=contentType)

def add_comment(request):
    result = imageHandler.add_comment(request.GET)
    return HttpResponse(json.dumps(result), content_type="application/json")

def image_detail(request):
    return HttpResponse(imageHandler.get_detail(request.GET),
                        content_type="text")

def search(request):
    return render(request,"search.html")

def search_result(request):
    resultDict = imageHandler.search_image(request.GET)
    return render(request, 'search_result.html', dictionary=resultDict)
