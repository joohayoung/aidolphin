from django.shortcuts import render, get_object_or_404
from mainapp.models import MusicDB, Comment, User

# Create your views here.

def about(request):
    return render(request, 'subapp/about.html')

def search(request):
    return render(request, 'subapp/search.html')

def test(request):
    # app별로 html파일이 있기때문에 " 앱이름/~.html " 로 경로지정해야함!
    return render(request, 'subapp/test.html')

def mypage(request):
    return render(request, 'subapp/mypage.html')