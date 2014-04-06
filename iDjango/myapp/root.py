from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
import imageHandler
import json # for AJAX
from forms import ImageUploadForm, CommentUploadForm, AjaxCommentForm

def index(request):
    return render(request,'index.html')

def upload(request):
    return render(request,'upload.html')

def upload_receive(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            imageHandler.add_image_from_form(form.cleaned_data)
        else:
            print "Evil or stupid: Invalid form when upload image"
    else:
        return HttpResponseForbidden('allowed only via POST')
    
    return HttpResponseRedirect('/')

def image_raw(request):
    img, contentType = imageHandler.get_image_from_form(request.GET)
    return StreamingHttpResponse(img.read(), content_type=contentType)
    
def image(request, imgNum):
    imgDict = imageHandler.get_metadata({"i" : imgNum})
    return render(request,'image.html', dictionary=imgDict)

def image_latest(request):
    imgNum = imageHandler.get_latest_num()
    return HttpResponseRedirect('/image/' + str(imgNum))

def image_list(request):
    imgDict = imageHandler.get_detail_dict()
    return render(request, 'image_list.html', dictionary=imgDict)

def image_thumbnail(request):
    img, contentType = imageHandler.get_thumbnail_from_form(request.GET)
    return StreamingHttpResponse(img.read(), content_type=contentType)

def add_comment(request):
    form = CommentUploadForm(request.GET)
    if form.is_valid():
        flag = imageHandler.add_comment(form.cleaned_data)
        return HttpResponse(flag, content_type="text")
    else:
        print "Invalid form when upload comment: Can be used for refresh"
        return HttpResponse("fail", content_type="text")

def ajax_comment(request):
    form = AjaxCommentForm(request.GET)

    if form.is_valid():
        comments, cType = imageHandler.get_comment_list(form.cleaned_data)
        return HttpResponse(comments, content_type=cType)
    else:
        print "Invalid ajax comment form"
        return HttpResponse(str(form.errors), content_type="text/html")
    
def search(request):
    return render(request,"search.html")

def search_result(request):
    resultDict = imageHandler.search_image(request.GET)
    return render(request, 'search_result.html', dictionary=resultDict)
