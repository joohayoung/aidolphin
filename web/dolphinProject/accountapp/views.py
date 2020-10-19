from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

# Create your views here.

def sign_up(request):
    context={}
    # POST Method
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        password_check = request.POST['password_check']

        # 제대로 입력되었을 경우
        if (username and password and password_check == password):
            new_user = User.objects.create_user(
                username = username,
                password = password,
            )
            # 로그인후 home을 redirect
            auth.login(request, new_user)
            return redirect('mainapp:home')
        else:
            context['error'] = "아이디와 비밀번호를 다시 확인해주세요."

    # GET Method
    return render(request, 'accountapp/sign_up.html', context)

def login(request):
    context={}

    # POST Method
    if request.method == "POST"
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(
                request,
                username = username,
                password = password
            )
            if user is not None:
                # 사용자가 있으면 로그인후 home으로
                auth.login(request, user)
                return redirect('mainapp:home')
            else:
                context['error'] = '아이디와 비밀번호를 다시 확인해주세요.'
        else:
            #아이디나 비밀번호가 제대로 입력되지 않았을때
            context['error'] = '아이디와 비밀번호를 모두 입력해주세요.'

    # Get Method
    return render(request, 'accountapp/login.html', context)

def logout(request):
    if request.method == "POST"
        auth.logout(request)
    # 로그아웃하면 홈으로
    return redirect("mainapp:home")