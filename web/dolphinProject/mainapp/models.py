from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class MusicDB(models.Model):
    fname = models.CharField(max_length=30)
    label = models.CharField(max_length=30)
    licenses = models.CharField(max_length=50) 
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts',blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField()
    downloads = models.IntegerField()

    def __str__(self):
        return f'{self.id}: {self.fname}'


class Comment(models.Model):
    music=models.ForeignKey(MusicDB, on_delete=models.CASCADE, related_name='comments')
    author=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add = True)