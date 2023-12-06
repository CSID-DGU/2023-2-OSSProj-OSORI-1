# 파이썬 라이브러리
import json
import datetime
from collections import defaultdict
# 장고 관련 참조
from django.shortcuts import render, redirect
from django.contrib import messages
# 모델 참조
from django.db.models import Count, Sum
from ..models import *


# ---------------------------------------------------- ( 렌더링 함수 ) ----------------------------------------------------------------

def r_head(request):
    return render(request, "head.html")

def addComma(num):
    return format(num, ',d')


def r_statistics(request):
    user_num = UserInfo.objects.count()
    major_num = UserInfo.objects.values('major').distinct().count()
    context = {
        'user_num' : user_num,
        'major_num' : major_num,
    }
    return render(request, "statistics.html", context)

def r_statistics_ge(request):
    user_num = UserInfo.objects.count()
    major_num = UserInfo.objects.values('major').distinct().count()
    context = {
        'user_num' : user_num,
        'major_num' : major_num,
    }
    return render(request, "statistics_ge.html", context)

def r_login(request):
    request.session.clear()
    return render(request, "login.html")

def r_login1(request):
    request.session.clear()
    return render(request, "login_admin.html")

def r_agree(request):
    target_qeuryset = Standard.objects.only('user_year', 'user_dep')
    # { 학과 : [21, 20 ...] }
    dict_dep_yearlist = defaultdict(lambda:'')
    for row in target_qeuryset:
        if row.user_dep not in dict_dep_yearlist.keys():
            dict_dep_yearlist[row.user_dep] += str(row.user_year)
        else:
            dict_dep_yearlist[row.user_dep] += ', ' + str(row.user_year)
    # 지원 학과 개수
    dep_num = len(dict_dep_yearlist.keys())
    # [ 학과, '21,20....' ] => 정렬
    target_list = [[ dep, year] for dep, year in dict_dep_yearlist.items()]
    target_list = sorted(target_list, key=(lambda x: x[0]))
    context = {
        'target' : target_list,
        'dep_num' : dep_num
    }
    return render(request, "agree.html", context)

def r_register(request):
    return render(request, "register.html")
def r_admin_(request):
    return render(request, "admin.html")

def r_success(request):
    temp_user_info = request.session.get('temp_user_info')
    if not temp_user_info :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    request.session.clear()
    return render(request, 'success.html')

def r_changePW(request):
    temp_user_id = request.session.get('temp_user_id')
    if not temp_user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    return render(request, 'changePW.html')

def r_mypage(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    try:
        ui_row = UserInfo.objects.get(student_id=user_id)
        mypage_json = ui_row.mypage_json
        # user_info DB에서 json을 꺼내 context 딕셔너리에 저장
        # context = json.loads(ui_row.mypage_json)
        if mypage_json:
            context = json.loads(mypage_json)
        else:
            context = {}
        return render(request, "mypage.html", context)
    except Exception as e:
        messages.error(request, f'❌ 오류 발생: {str(e)}')
        return redirect('/')

def r_custom(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    # 그냥 mypage json을 넘겨주고 거기서 성적표 뽑아쓰자. (DB히트 감소)
    ui_row = UserInfo.objects.get(student_id = user_id)
    mypage_context = json.loads(ui_row.mypage_json)
    context = {
        'grade' : mypage_context['grade'],
        'custom_grade' : mypage_context['custom_grade'],
    }
    return render(request, "custom.html", context)

def r_success_delete(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    request.session.clear()
    return render(request, 'success_delete.html')

def r_result(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    ui_row = UserInfo.objects.get(student_id = user_id)
    context = json.loads(ui_row.result_json)
    return render(request, "result.html", context)

def r_multi_result(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    ui_row = UserInfo.objects.get(student_id = user_id)
    context = json.loads(ui_row.result_json)
    return render(request, "multi_result.html", context)

def r_en_result(request):
    user_id = request.session.get('id')
    if not user_id :
        messages.error(request, '❌ 세션 정보가 없습니다!')
        return redirect('/')
    ui_row = UserInfo.objects.get(student_id = user_id)
    context = json.loads(ui_row.en_result_json)
    return render(request, "en_result.html", context)
