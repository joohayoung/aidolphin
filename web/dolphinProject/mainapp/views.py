from django.shortcuts import render
from .models import MusicDB
from django.db.models import Q, Count
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