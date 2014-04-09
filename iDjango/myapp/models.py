from django.db import models
from PIL import ImageFile # for generating thumbnail
from StringIO import StringIO # for buffer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import formats

# Default no preview thumbnail (default format is png)
DefaultThumbnail = "image/no_preview.png"

# Default Thumbnail size
ThumbnailSize = 70, 70

class MyImageManager(models.Manager):

    def meta(self):
        return self.values("id", "name", "description")
        
class MyImage(models.Model):
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='images/%Y', max_length=100)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y', max_length=100)
    description = models.CharField(max_length=256, null=True)
    sql = MyImageManager()
    
    # save thumbnail in PNG format
    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/
        
        if not self.image:
            return

        # read data into PIL image
        p = ImageFile.Parser()
        img = None
        try:
            p.feed(self.image.read())
            img = p.close()
        except Exception, msg:
            print "Cannot generate thumbnail for ", self.name, ":",  msg

        fp = None
        # if cannot read the image file using PIL
        if img == None:
            # generate a default thumbnail
            dirname = os.path.join(os.path.dirname(__file__),"")
            thumbnail_path = os.path.join(dirname, DefaultThumbnail)
            fp = open(thumbnail_path, 'rb').read()
        else:
            # generate an actual thumbnail
            fp = StringIO()
            img.thumbnail(ThumbnailSize)
            img.save(fp, format="PNG")
            fp.seek(0)
            
        suf = SimpleUploadedFile(self.name, fp.read(), content_type='image/png')
         
        # Save SimpleUploadedFile into image field
        self.thumbnail.save('%s_thumbnail.png'%(self.name), suf, save=False)
    
    def __str__(self):
        return self.name

    def save(self):
        # create a thumbnail
        self.create_thumbnail()
        super(MyImage, self).save()

class MyComment(models.Model):
    comment = models.CharField(max_length=300, null=True)
    imageId = models.PositiveIntegerField(null=True)
    user = models.CharField(max_length=100, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __str__(self):
        temp = "Comment from " + self.user
        temp += " to image " + str(self.imageId)
        return temp

    def as_json(self):
        jsonDict = dict(
            user=self.user,
            comment=self.comment, 
            datetime=formats.date_format(self.datetime)
            )
        return jsonDict
