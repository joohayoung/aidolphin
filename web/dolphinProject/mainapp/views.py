from django.shortcuts import render, redirect
from .models import MusicDB, UploadMusicDB, UserMusicDB
from django.db.models import Q, Count
from django.http import HttpResponse
import json
from django.contrib.auth.decorators import login_required
from similarModel.similarmodel import similarAnalysis
from model.type_predictor import label_type
from model.mood_predictor import mood_type

# Create your views here.

def home(request):
    return render(request, 'mainapp/home.html')

@login_required(login_url='/accountapp/login')
def upload(request):
    context = {}
    if request.method=='POST':
        if 'file' in request.FILES :
            ## 파일을 music_sample에 저장
            audio = request.FILES['file']
            userfile = UserMusicDB(audio=audio)
            userfile.save()

            ##파일정보를 DB에 저장
            fname = request.POST.get('fname_', '')
            if fname =='rename':
                fname = request.POST.get('fname_')
            else:
                fname = audio.name

            print(fname)

            label = request.POST.get('label')
            if label == 'self':
                label = request.POST.get('label_')
            else:
                # label = 'Telephone' #확인용
                file_path = f"media/music_sample/{audio}"
                label = label_type(file_path)#모델이용하기

            licenses = request.POST.get('license')
            
            author_op = request.POST.get('author')
            author = request.user
            if author_op == 'user_':
                real_author = request.user.username
            elif author_op == 'author':
                real_author = request.POST.get('author_')
            else :
                newmusic = MusicDB(fname = fname, label = label, licenses = licenses, downloads = 0)
                newmusic.save()
                return redirect('mainapp:home') # 또는 마이페이지?

            newmusic = MusicDB(fname = fname, label = label, licenses = licenses,
            downloads = 0, author = author)
            newmusic.save()

            linkpk = MusicDB.objects.get(fname=fname).pk
            return redirect('subapp:detail', linkpk )
            # return redirect('mainapp:home') # 또는 마이페이지?
        else:
            context['error'] = '파일 입력 없음'
    else:
        pass

    return render(request, 'mainapp/upload.html', context)


def realtime(request):
    context = {}
    if request.method=='POST':
        if 'file' in request.FILES:
            audio = request.FILES['file']
            uploadfile = UploadMusicDB(audio=audio)
            uploadfile.save()
            context['audio'] = audio.name
            # print('views.py realtime audioname : ', audio.name)

            # audio 파일을 모델 함수에 입력 아웃풋 lagel값
            file_path = f"media/upload_music/{audio}"
            label = label_type(file_path) # 모델활용
            # label = 'Telephone' #확인용
            context['label'] = label

            # 분위기 분류
            mood = mood_type(file_path)
            # mood = 'test' #확인용
            context['mood'] = mood #모델활용
            
            # 파일을 지우기 전에 유사도 분석까지 해야한다
            # similarlist = similarAnalysis(audio.name)
            # #############################################################################
            # music_list = MusicDB.objects.filter(fname = similarlist[0])
            # for name in similarlist[1:] :
            #     item = MusicDB.objects.filter(fname = name)
            #     # music_list = music_list.union(item)
            #     music_list = music_list | item
            # context['similarlist'] = music_list #similarlist
            #############################################################################

            uploadfile.delete()
        else:
            context['audio'] = 'audio_none'
            context['label'] = 'label_none'
            context['mood'] = 'mood_none'
    else:
        context['audio'] = 'audio_none'
        context['label'] = 'label_none'
        context['mood'] = 'mood_none'

    return HttpResponse(json.dumps(context))

def search(request):
    context = {}
    audio = None
    label = None
    search_type = None
    similarlist = None
    check = True
    mood = None

    ####파일검색(최초)
    if request.method=='POST':
        if 'file' in request.FILES:
            audio = request.FILES['file']
            uploadfile = UploadMusicDB(audio=audio)
            uploadfile.save()

            context['audio'] = audio
            # audio 파일을 모델 함수에 입력 아웃풋 lagel값
            file_path = f"media/upload_music/{audio}"
            label = label_type(file_path) # 모델활용
            # label = 'Telephone' #확인용
            context['label'] = label

            mood = mood_type(file_path)
            # mood = 'test' #확인용
            context['mood'] = mood #모델활용

            # 파일을 지우기 전에 유사도 분석까지 해야한다
            similarlist = similarAnalysis(audio.name) 
            # context['similarlist'] = similarlist   
            check = False        
            uploadfile.delete()
            
            search_type='filesearch'
            context['search_type'] = search_type
    else:
        label = request.GET.get('label', '')
        context['label'] = label
        audio = request.GET.get('audio', '')
        context['audio'] = audio
        mood = request.GET.get('mood', '')
        context['mood'] = mood

    ### GET 요청으로 들어올 경우 ##############################################
    if search_type == None:
        search_type = request.GET.get('search_type', 'keyword')
        context['search_type'] = search_type

    if (search_type == 'filesearch')  : #or (search_type == 'realtimesearch')
        if check:
            music_list = request.GET.get('similarlist')
            context['similarlist'] = music_list
            print("파일검색전달 or 실시간 검색 객체 불러오기 완료")

        else: #첫 파일 검색일 경우 
            music_list = MusicDB.objects.filter(fname = similarlist[0])
            for name in similarlist[1:] :
                item = MusicDB.objects.filter(fname = name)
                # music_list = music_list.union(item)
                music_list = music_list | item
            context['similarlist'] = music_list 
            print('첫 파일 검색 유사도 정렬 완료')

        sort = request.GET.get('sort', 'similar') #나중에 기본설정 similar로 바꾸기
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = music_list.annotate(num_like=Count('like')).order_by('-num_like','-date')
        elif sort == 'download': #다운로드순
            music_list = music_lists.order_by('-downloads', '-date')
        elif sort == 'similar': #유사도(기본)
            pass
        else: #recent 최신순 
            music_list = music_lists.order_by('-date')

        print("파일/실시간 검색 sort 적용")
        
    else: #키워드 검색일때 (+ 유사도 안되는 실시간)
        ## DB 불러와서 정렬하기
        sort = request.GET.get('sort', 'like') # 키워드 검색은 기본 좋아요로 검색
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = MusicDB.objects.annotate(num_like=Count('like')).order_by('-num_like','-date')
        elif sort == 'download': #다운로드순
            music_list = MusicDB.objects.order_by('-downloads', '-date')
        else: #recent 최신순 or 유사도
            music_list = MusicDB.objects.order_by('-date')


    ## 검색결과
    kw = request.GET.get('kw', '')
    context['kw'] = kw

    # if label: #키워드 검색이 아니고 파일검색에서 라벨을 입력(?)받았을때
    #     kw = label 

    if kw != '' : # 키워드 검색 파일명이나 라벨명으로 검색
        music_list = music_list.filter(
            Q(fname__contains=kw) | Q(label__contains=kw)
        )#.distinct()
    elif label: #kw가 ''인데 label 값이 있을경우 label로 검색
        music_list = music_list.filter(label__contains=label)#.distinct()
    else:
        #kw가 ''이고 label값도 없을경우 => 키워드검색, 키워드 입력안함 => 전체 
        pass
    
    print('라벨필터링 완료')
    # name_list = []
    # for item in music_list:
    #     name_list.append(item.fname)
    # context['name_list'] = name_list


    ## 라이센스 필터링
    licenses = request.GET.getlist('license[]', 'all')
    # print(licenses)
    if 'all' in licenses:
        #all 이 같이 입력되거나 아무것도 입력되지 않았을때
        context['license']='all'
        
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

        if 'work' in licenses:
            # 변경가능 : cc0 / by-nc / by-sa / by-nc-sa / by
            # 변경불가능 : by-nd / by-nc-nd
            music_list = music_list.exclude(licenses__contains='Derivative Works')

    print('라이센스필터링 완료')
    context['music_list'] = music_list
    return render(request, 'mainapp/search.html', context)