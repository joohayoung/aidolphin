from django.contrib import admin
from .models import MusicDB, UploadMusicDB

# Register your models here.
admin.site.register(MusicDB)
admin.site.register(UploadMusicDB)