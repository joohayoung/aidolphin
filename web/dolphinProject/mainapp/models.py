from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings
# Create your models here.

class MusicDB(models.Model):
    fname = models.CharField(max_length=30)
    label = models.CharField(max_length=30)
    licenses = models.CharField(max_length=50) 
    like = models.ManyToManyField(User, related_name='liked_posts')
    date = models.DateTimeField(auto_now_add=True)
    downloads = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) #등록자 admin
    real_author = models.CharField(max_length=30, null=True) #작가 license 가진사람????
    mood = models.CharField(max_length=30) #분위기값

    def __str__(self):
        return f'{self.id}: {self.fname}'

class UploadMusicDB(models.Model):
    audio = models.FileField(upload_to='upload_music')
    # audio = models.FileField(blank=True, upload_to='upload_music/%Y/%m/%d')

    def __str__(self):
        return f'{self.id}: {self.audio}'

    def delete(self, *args, **kwargs):
        #media>upload_music 자동삭제
        super(UploadMusicDB, self).delete(*args, **kwargs)
        os.remove(os.path.join(settings.MEDIA_ROOT, self.audio.path))

#--------------------------------------------------#
class Comment(models.Model):
    music=models.ForeignKey(MusicDB, on_delete=models.CASCADE, related_name='comments')
    author=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add = True)


class UserMusicDB(models.Model):
    audio = models.FileField(upload_to='music_sample')

    def __str__(self):
        return f'{self.id}: {self.audio}'

    def delete(self, *args, **kwargs):
        super(UserMusicDB, self).delete(*args, **kwargs)
        os.remove(os.path.join(settings.MEDIA_ROOT, self.audio.path))
