from django.db import models

class Image(models.Model):
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d', max_length=100)
    description = models.CharField(max_length=256, null=True)
