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
            ).distinct()

        ## 라이센스 필터링
        licenses = request.GET.getlist('license[]', 'all')
        print(licenses)
        if 'all' in licenses:
            #all 이 같이 입력되거나 아무것도 입력되지 않았을때
            context['license']='all'
            context['music_list'] = music_list
        else:
            context['license'] = licenses
            # BY Attribution
            # NC Noncommercial
            # ND (No)Derivative Works
            # SA Share-Alike
            # CC0 Creative Commons 0

            ### licenses = [CC0 BY NC]
            q=['','','','','']
            if 'CC0' in licenses:
                q[0]='CreativeCommons0'
            else : q[0]='nonono'#없을것 임의로 임력

            if 'BY' in licenses:
                q[1]='Attribution'
            else: q[1]='nonono'

            if 'NC' in licenses:
                q[2]='Noncommercial'
            else: q[2]='nonono'

            if 'ND' in licenses:
                q[3]='DerivativeWorks'
            else: q[3]='nonono'

            if 'SA' in licenses:
                q[4]='Share-Alike'
            else: q[4]='nonono'

            print(q)
            context['music_list'] = music_list.filter(
                Q(licenses__contains=q[0])|
                Q(licenses__contains=q[1])|
                Q(licenses__contains=q[2])|
                Q(licenses__contains=q[3])|
                Q(licenses__contains=q[4])
            ).distinct()

    #context['license']='temp'
    return render(request, 'mainapp/search.html', context)