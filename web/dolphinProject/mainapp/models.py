from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class MusicDB(models.Model):
    fname = models.CharField(max_length=30)
    label = models.CharField(max_length=30)
    licenses = models.CharField(max_length=50) 
    like = models.ManyToManyField(User, related_name='liked_posts')
    date = models.DateTimeField()
    downloads = models.IntegerField()

    def __str__(self):
        return f'{self.id}: {self.fname}'

class UploadMusicDB(models.Model):
    audio = models.FileField(upload_to='upload_music')
    # audio = models.FileField(blank=True, upload_to='upload_music/%Y/%m/%d')

    def __str__(self):
        return f'{self.id}: {self.audio}'
