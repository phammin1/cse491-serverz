import quixote
from quixote.directory import Directory, export, subdir
import os # for absolute path
import json
from . import html, image

class RootDirectory(Directory):
    _q_exports = []

    @export(name='')                    # this makes it public.
    def index(self):
        return html.render('index.html')

    @export(name='upload_image')
    def upload_image(self):
        return html.render('upload.html')

    @export(name='upload_receive')
    def upload_receive(self):
        request = quixote.get_request()
        image.add_image_from_form(request.form)

        return quixote.redirect('./')

    @export(name='search_result')
    def search_result(self):
        request = quixote.get_request()
        resultDict = image.search_image(request.form)
        return html.render('search_result.html', resultDict)
        
    @export(name='image')
    def image(self):
        request = quixote.get_request()
        imgDict = image.get_metadata(request.form)
        return html.render('image.html', imgDict)

    @export(name='search')
    def search_image(self):
        return html.render('search.html')
    
    @export(name='image_raw')
    def image_raw(self):
        request = quixote.get_request()
        img, contentType = image.get_image_from_form(request.form)
        response = quixote.get_response()
        response.set_content_type(contentType)
        return img

    @export(name='image_thumbnail')
    def image_thumbnail(self):
        request = quixote.get_request()
        img, contentType = image.get_thumbnail_from_form(request.form)
        response = quixote.get_response()
        response.set_content_type(contentType)
        return img
    
    @export(name='image_detail')
    def image_detail(self):
        request = quixote.get_request()
        return image.get_detail(request.form)

    @export(name="image_list")
    def image_list(self):
	imgDict = image.get_detail_dict()
	return html.render('image_list.html', imgDict)


    @export(name="add_comment")
    def add_comment(self):
        request = quixote.get_request()
        result = image.add_comment(request.form)
        return json.dumps(result)

    @export(name="jquery")
    def jquery(self):
        # Credit to Xavier Durand Hollis
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname,"")
        jquery_path = os.path.join(dirname,'jquery-1.3.2.min.js')
        return open(jquery_path).read()
