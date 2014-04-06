from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

admin.autodiscover()

# List of page that are currently implement
PageList = ["upload", "upload_receive", "image_raw", "add_image",
                "image_list", "image_thumbnail", "add_comment",
            "search", "search_result", "ajax_comment"
            ]
RootFile = 'myapp.root'

customPatterns = [
    url(r'^image/latest/$', RootFile + '.image_latest', name='image'),
    url(r'^image/(\d{0,6})$', RootFile + '.image', name='image'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    ]

urlpatterns = [url(r'^$', RootFile + '.index', name='index')]

for page in PageList:
    reg = '^' + page + '/$'
    view = RootFile + '.' + page
    urlpatterns.append(url(reg, view, name=page))

urlpatterns += staticfiles_urlpatterns()
urlpatterns += customPatterns
