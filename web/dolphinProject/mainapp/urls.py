from django.urls import path 
from . import views

app_name = 'mainapp'
urlpatterns = [
    path('', views.home, name='home'), #127.0.0.1:8000/ 
    path('search/', views.search, name='search'),
    path('realtime/', views.realtime, name='realtime'),
]
