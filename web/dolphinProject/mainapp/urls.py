from django.urls import path 
from . import views

app_name = 'mainapp'
urlpatterns = [
    path('', views.home, name='home'), #127.0.0.1:8000/ 
    path('search/', views.search, name='search'),
    path('search/<int:MusicDB_id>/', views.detail, name='detail'),
    path('search/<int:pk>/like/', views.like, name='like'),
    path('<int:music_pk>/comments/new/', views.comments_new, name='comments_new'),
    path('<int:music_pk>/comments/<int:pk>/delete/', views.comments_delete, name = 'comments_delete'),
    path('<int:music_pk>/comments/<int:pk>/edit/', views.comments_edit, name ='comments_edit'),
]
