from django.urls import path 
from . import views

app_name = 'subapp'
urlpatterns = [
    path('about/', views.about, name='about'), #127.0.0.1:8000/subapp/about
    path('detail/', views.detail, name='detail'), 
    # 테스트 페이지
    path('test/', views.test, name='test'), #127.0.0.1:8000/subapp/test
]