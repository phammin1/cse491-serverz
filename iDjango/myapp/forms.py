from django import forms

# Datetime format receive from ajax query
AjaxUTCDateFormat = ["%a, %d %b %Y %H:%M:%S %Z"]
AjaxLocaleDateFormat = ["%a %d %b %Y %I:%M:%S %p %Z"]


class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()
    description = forms.CharField(max_length=100)

class CommentUploadForm(forms.Form):
    """Comment upload form"""
    comment = forms.CharField(max_length=300)
    user = forms.CharField(max_length=100)
    imageId = forms.IntegerField()

class AjaxCommentForm(forms.Form):
    """ Get comments using ajax """
    time = forms.FloatField()
    imageId = forms.IntegerField()
