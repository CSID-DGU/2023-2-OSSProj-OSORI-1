# 파이썬 라이브러리
import datetime
import bcrypt
import json
# 장고 관련 참조
from django.shortcuts import redirect
from django.contrib import messages
# 모델 참조
from ..models import *

def f_logout(request):
    request.session.clear()
    return redirect('/')

def f_login(request):
    # ID PW 넘어옴
    user_id = request.POST.get('id')
    pw = request.POST.get('pw')
    # 그 값으로 모델에서 행 추출
    ui_row = UserInfo.objects.filter(student_id=user_id)
    # 우선 회원가입 되지 않았다면?
    if not ui_row.exists():
        messages.error(request, '⚠️ Graduate is Good에 가입되지 않은 ID입니다.')
        return redirect('/login/')
    # 회원인데 비번이 틀렸다면? 입력받은 비번을 암호화하고 DB의 비번과 비교한다.
    if not bcrypt.checkpw(pw.encode('utf-8'), ui_row[0].password.encode('utf-8')):
        messages.error(request, '⚠️ Graduate is Good 비밀번호를 확인하세요.')
        return redirect('/login/')
    # !! 로그인시마다 json을 최신화시킨다 !!
    update_json(user_id)
    # 세션에 ID 저장
    request.session['id'] = user_id
    return redirect('/mypage/')

def f_mypage(user_id):
    ui_row = UserInfo.objects.get(student_id=user_id)
    ug = UserLecture.objects.filter(student_id=user_id)
    # 만약 성적표 업로드 안했다면
    is_grade = 1
    if not ug.exists():
        is_grade = 0

    mypage_context ={
        'student_id' : ui_row.student_id,
        'email' : ui_row.email,
        'major' : ui_row.major,
        'sub_major' : ui_row.sub_major,
        'name' : ui_row.name,
        'eng' : ui_row.eng,
        'is_grade' : is_grade,
    }
    return mypage_context

def update_json(user_id):
    ui_row = UserInfo.objects.get(student_id = user_id)
    # mypage json 업데이트
    mypage_context = f_mypage(user_id)
    ui_row.mypage_json = json.dumps(mypage_context)
    return