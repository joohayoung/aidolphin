from django.urls import path 
from . import views

from django.conf.urls.static import static
from django.conf import settings

app_name = 'subapp'
urlpatterns = [
    path('about/', views.about, name='about'), #127.0.0.1:8000/subapp/about
    path('mypage/', views.mypage, name='mypage'),

    path('<int:MusicDB_id>/', views.detail, name='detail'),
    path('<int:pk>/like/', views.like, name='like'),
    path('<int:music_pk>/comments/new/', views.comments_new, name='comments_new'),
    path('<int:music_pk>/comments/<int:pk>/delete/', views.comments_delete, name = 'comments_delete'),
    path('<int:music_pk>/comments/<int:pk>/edit/', views.comments_edit, name ='comments_edit'),
    path('downloads', views.downloads, name='downloads'),
    path('profile/<username>/', views.profile, name='profile'),
    path('test/', views.test, name='test'), #127.0.0.1:8000/subapp/test
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)