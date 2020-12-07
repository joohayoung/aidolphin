from django.contrib import admin
from .models import MusicDB, UploadMusicDB, Comment, UserMusicDB

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'fname', 'user', 'date',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'id','music','text', 'author','date',)

admin.site.register(MusicDB)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UploadMusicDB)
admin.site.register(UserMusicDB)