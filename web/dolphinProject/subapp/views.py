from django.shortcuts import render,get_object_or_404,redirect
from mainapp.models import MusicDB,Comment,Profile,User
from django.db.models import Q, Count
from mainapp.forms import CommentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import math
# Create your views here.

def about(request):
    return render(request, 'subapp/about.html')

def detail(request,MusicDB_id):
    music= get_object_or_404(MusicDB, pk=MusicDB_id)
    comment_form = CommentForm()
    comments = music.comments.all()
    #comments=Comment.objects.all()
    context = {
        'music':music,
        'comment_form': comment_form,
        'comments':comments,
    }
    return render(request,'subapp/detail.html',context)

@login_required(login_url='/accountapp/login')
def like(request,pk):
    musicdb = get_object_or_404(MusicDB, pk=pk)
    
    if request.user in musicdb.like.all():
            #좋아요 취소
        musicdb.like.remove(request.user)
    else:
        musicdb.like.add(request.user)
        
    return redirect('subapp:detail', musicdb.pk)

@login_required(login_url='/accountapp/login')
def comments_new(request, music_pk): #POST 
    # 1. 요청이 POST 인지 점검
    if request.method  == 'POST': 
        # 2. form에 data를 집어넣기 (목적 == 유효성 검사)
        form = CommentForm(request.POST)
        # request.POST #=>
        # 3. form에서 유효성 검사를 시행
        if form.is_valid():
            # 4. 통과하면 database에 저장 
            comment = form.save(commit=False)
            # 4-1. article 정보 주입
            comment.music_id = music_pk
            comment.author = request.user 
            comment.save()
    # 5. 생성된 댓글을 확인할 수 있는 곳으로 안내 
    return redirect('subapp:detail', music_pk)

@login_required(login_url='/accountapp/login')
def comments_delete(request, music_pk, pk): # POST 
    # 0. 요청이 POST인지 점검 
    if request.method == 'POST':
        # 1. pk를 가지고 삭제하려는 data를 꺼내오기 
        comment = Comment.objects.get(pk=pk)
        # 2. 삭제
        comment.delete()
    # 3. 삭제되었는지 확인 가능한 곳으로 안내 
    
    return redirect('subapp:detail', music_pk)
    
@login_required(login_url='/accountapp/login')
def comments_edit(request,music_pk, pk): # GET , POST 
    # Database에서 수정하려 하는 data 가져오기 
    comment = Comment.objects.get(pk=pk)

    # 수정권한 확인
    if request.user != comment.author:
        messages.error(request, '수정권한이 없습니다.')
        return redirect('subapp:detail', music_pk)

    # 0. 요청의 종류가 POST인지 GET인지 점검 
    if request.method == 'POST':
        # 실제로 수정 ! 
        # 1. form에 '넘어온 data' & '수정하려는 data' 집어넣기 
        form = CommentForm(request.POST, instance=comment)
        # 2. 유효성 검사 
        if form.is_valid():
            # 3. 검사를 통과했다면, save 
            comment = form.save()
            # 4. 변경된 결과 확인하는 곳으로 안내 
            return redirect('subapp:detail', music_pk)
    else : 
        # 수정 양식 보여주기! 
        # 1. form class 초기화 (생성)
        form = CommentForm(instance=comment)

    context ={
        'form' : form,
    }
    return render(request,'subapp/comments_edit.html', context)

def downloads(request):
    if request.method=='POST':
        pk = request.POST.get('music_id')
        music = MusicDB.objects.get(pk=pk)
        temp = music.downloads
        music.downloads = temp + 1
        music.save()

    return redirect('subapp:detail', pk)

def mypage(request):
    return render(request, 'subapp/mypage.html')
    
def test(request):
    # app별로 html파일이 있기때문에 " 앱이름/~.html " 로 경로지정해야함!
    return render(request, 'subapp/test.html')

# @login_required
def profile(request, username):
    context={}
    # 옵션값 가져오기
    sort = request.GET.get('sort', 'recent')
    context['sort'] = sort
    page = int(request.GET.get('page', 1))
    context['page'] = page
    paginated_by = 20
    #객체들 가져오기
    user = get_object_or_404(User, username=username)
    context['user'] = user
    profile = get_object_or_404(Profile, user=user)
    context['profile'] = profile
    musicdb = MusicDB.objects.filter(author=user)
    follow = profile.follow.all()
    context['follow'] = follow
    #뮤직DB정렬
    if sort == "like":
        musicdb = musicdb.annotate(num_like=Count('like')).order_by('-num_like','-date')
    elif sort == "downloads":
        musicdb = musicdb.order_by('-downloads', '-date')
    else : #recent:
        musicdb = musicdb.order_by('-date')
    #페이징
    start_idx = paginated_by * (page-1)
    end_idx = paginated_by * page
    total_count = musicdb.count()

    musicdb = musicdb[start_idx:end_idx]
    context['musicdb'] = musicdb

    total_page = math.ceil( total_count / paginated_by) 
    if page == 1 or page==2 or page==3: #첫페이지일때
        page_range = range(2, 7)
    elif page == total_page or page == total_page -1 or page == total_page -2 : #마지막 페이지 일때
        page_range = range(total_page-5, total_page)
    else:
        page_range = range(page-2, page+3)
    
    context['totalpage'] = total_page
    context['page_range'] = page_range

    return render(request,'subapp/profile.html', context)

@login_required(login_url='/accountapp/login')
def follow(request, username):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, username=username)
            profile = get_object_or_404(Profile, user=user)

            if request.user in profile.follow.all():
                profile.follow.remove(request.user)
            else:
                profile.follow.add(request.user)

            return redirect('subapp:profile', username)
        
        except Profile.DoesNotExist:
            pass

    return redirect('mainapp:home')
