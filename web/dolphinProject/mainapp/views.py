from django.shortcuts import render,get_object_or_404,redirect
from .models import MusicDB,Comment
from django.db.models import Q, Count
from .forms import CommentForm
# Create your views here.

def home(request):
    return render(request, 'mainapp/home.html')

def search(request):
    context = {}

    if request.method == "GET":
        ## 정렬하기
        sort = request.GET.get('sort', 'like') #나중에 기본설정 similar로 바꾸기
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = MusicDB.objects.annotate(num_like=Count('like')).order_by('-num_like','-date')
        elif sort == 'download': #다운로드순
            music_list = MusicDB.objects.order_by('-downloads', '-date')
        elif sort == 'similar': #유사도(기본)
            #유사도 추가하기
            pass
        else: #recent 최신순
            music_list = MusicDB.objects.order_by('-date')

        ## 검색결과
        kw = request.GET.get('kw', '')
        context['kw'] = kw

        if kw != '' :
            music_list = music_list.filter(
                Q(fname__contains=kw) | Q(label__contains=kw)
            )#.distinct()

        ## 라이센스 필터링
        licenses = request.GET.getlist('license[]', 'all')
        print(licenses)
        if 'all' in licenses:
            #all 이 같이 입력되거나 아무것도 입력되지 않았을때
            context['license']='all'
            context['music_list'] = music_list
        else:
            context['license'] = licenses
            # author commercial work
            if 'author' in licenses:
                #저작자 표기안함 : cc0
                music_list = music_list.filter(licenses='CreativeCommons0')
            
            if 'commercial' in licenses:
                # 상업적 이용가능 : cc0 / by-nb / by-sa / by
                # by-nc / by-nc-sa / by-nc-nd
                music_list = music_list.exclude(licenses__contains='Noncommercial')
                # music_list = music_list.filter(
                #     Q(licenses='CreativeCommons0')|
                #     Q(licenses='Attribution Derivative Works')|
                #     Q(licenses='Attribution Share-alike')|
                #     Q(licenses='Attribution')
                # )

            if 'work' in licenses:
                # 변경가능 : cc0 / by-nc / by-sa / by-nc-sa / by
                # 변경불가능 : by-nd / by-nc-nd
                music_list = music_list.exclude(
                    licenses__contains='Derivative Works'   
                )

            context['music_list'] = music_list

    return render(request, 'mainapp/search.html', context)

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
    return render(request,'mainapp/detail.html',context)

def like(request,pk):
    musicdb = get_object_or_404(MusicDB, pk=pk)
    
    if request.user in musicdb.like.all():
            #좋아요 취소
        musicdb.like.remove(request.user)
    else:
        musicdb.like.add(request.user)
        
    return redirect('mainapp:detail', musicdb.pk)


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
            comment.save()
    # 5. 생성된 댓글을 확인할 수 있는 곳으로 안내 
    return redirect('mainapp:detail', music_pk)

def comments_delete(request, music_pk, pk): # POST 
    # 0. 요청이 POST인지 점검 
    if request.method == 'POST':
        # 1. pk를 가지고 삭제하려는 data를 꺼내오기 
        comment = Comment.objects.get(pk=pk)
        # 2. 삭제
        comment.delete()
    # 3. 삭제되었는지 확인 가능한 곳으로 안내 
    
    return redirect('mainapp:detail', music_pk)

def comments_edit(request,music_pk, pk): # GET , POST 
    # Database에서 수정하려 하는 data 가져오기 
    comment = Comment.objects.get(pk=pk)
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
            return redirect('mainapp:detail', music_pk)
    else : 
        # 수정 양식 보여주기! 
        # 1. form class 초기화 (생성)
        form = CommentForm(instance=comment)

    context ={
        'form' : form,
    }
    return render(request,'mainapp/comments_edit.html', context)





