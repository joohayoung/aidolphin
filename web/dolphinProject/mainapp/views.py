from django.shortcuts import render
from .models import MusicDB
from django.db.models import Q, Count
# Create your views here.

def home(request):
    return render(request, 'mainapp/home.html')

def search(request):
    context = {}

    if request.method == "GET":
        # 필터링 / 정렬
        ## 정렬하기
        sort = request.POST.get('sort', 'like') #나중에 기본설정 similar로 바꾸기
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = MusicDB.objects.annotate(num_like=Count('like')).order_by('-date')
        elif sort == 'download': #다운로드순
            music_list = MusicDB.objects.annotate(num_downloads=Count('downloads')).order_by('-date')
        elif sort == 'similar': #유사도(기본)
            #유사도 추가하기
            pass
        else: #recent 최신순
            music_list = MusicDB.objects.order_by('-date')

        # 검색결과
        kw = request.GET.get('kw', '')
        context['kw'] = kw

        if kw != '' :
            context['music_list'] = music_list.filter(
                Q(fname__contains=kw) | Q(label__contains=kw)
            )#.distinct()
        else:
            context['music_list']=None


    context['license']='temp'
    return render(request, 'mainapp/search.html', context)