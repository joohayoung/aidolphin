from django.urls import path
from . import views

app_name = 'accountapp'
urlpatterns = [
    path('sign_up/', views.sign_up, name='sign_up'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
]