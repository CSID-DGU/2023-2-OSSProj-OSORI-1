# 파이썬 라이브러리
import json
import openpyxl
import pandas as pd
import bcrypt
# 장고 관련 참조
from django.shortcuts import redirect
from django.contrib import messages
# 모델 참조
from ..models import *
from .auth import *


def f_mod_info_ms(request):
    user_id = request.session.get('id')
    ui_row = UserInfo.objects.get(student_id = user_id)
    ui_row.major = request.POST.get('major_select')
    ui_row.save()
    update_json(user_id)
    del request.session['temp_major_select']
    messages.success(request, '업데이트성공')
    return redirect('/mypage/') 

# 1. 내정보 수정
def f_mod_info(request):
    user_id = request.session.get('id')
    pw = request.POST.get('pw')
    # 기본 정보 -> 변수에 저장
    ui_row = UserInfo.objects.get(student_id = user_id)
    
    # 유저정보 테이블에 저장 후 json DB도 업데이트
    ui_row.save()
    update_json(user_id)
    messages.success(request, '업데이트성공')

    return redirect('/mypage/') 


# 2. 전공상태 + 영어인증 수정
def f_mod_ms_eng(request):
    # 세션id, 입력받은 값 꺼내기
    user_id = request.session.get('id')
    major_status = request.POST.get('major_status')
    eng = request.POST.get('eng')
    if eng not in ['해당없음', '초과학기면제', '영어인증면제학과']:
        eng = eng + '/' + str(request.POST.get('eng_score'))
    # 사용자의 user_info row 부르기
    ui_row = UserInfo.objects.get(student_id = user_id)
    # 변경시에만 다시 저장
    if ui_row.eng != eng or ui_row.major_status != major_status:
        # 수정된 DB 넣고 save
        ui_row.eng = eng
        ui_row.major_status = major_status
        ui_row.save()
        # json DB도 업데이트
        update_json(user_id)
    messages.success(request, '업데이트성공')
    return redirect('/mypage/') 

# 3. 비밀번호 수정
def f_mod_pw(request):
    # 수정은 두가지 -> 로그인전과 로그인 후
    if request.session.get('id') != None:
        user_id = request.session.get('id')
    else:
        user_id = request.POST.get('id')
    # 암호화
    password = request.POST.get('password')
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    
    password = password.decode('utf-8')                                     
    # 저장
    ui_row = UserInfo.objects.get(student_id = user_id)
    ui_row.password = password
    ui_row.save()
    messages.success(request, '업데이트성공')
    if request.session.get('id') != None:
        return redirect('/mypage/')
    else:
        return redirect('/login/')
#4 관심과목 장바구니
def f_mod_cart(request):
        return redirect('/mypage/')

# 4. 기이수과목 수정
def f_mod_grade(request):
    # 넘겨받은 파일 꺼내기
    excel = request.FILES['excel']

    # 검사1 : 엑셀파일인지 검사
    if excel.name[-4:] != 'xlsx':
        messages.error(request, '⚠️ 잘못된 파일 형식입니다. 확장자가 xlsx인 파일을 올려주세요. ')
        return redirect('/mypage/')
    try:
        # 엑셀 파일을 수정해줘야함
        wb = openpyxl.load_workbook(excel)
        ws = wb.active
        # 엑셀을 df로 변환
        df = pd.DataFrame(ws.values)
        # 첫 행을 컬럼으로 지정
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]
        df = df.drop(['번호'], axis=1)
        df = df.drop([''],axis=1)
    except:
        messages.error(request, '⚠️ 엑셀 내용이 다릅니다! 수정하지 않은 엑셀파일을 올려주세요.')
        return redirect('/mypage/')

    # 검사2 : 형식에 맞는지 검사
    if list(df.columns) != ['년도', '학기', '이수구분', '이수구분영역', '학수강좌번호', '교과목명', '담당교원', '학점', '등급', '삭제구분', '재수강구분', '공학인증', '공학요소', '공학세부요소', '원어강의종류', '인정구분', '성적인정대학명', '교과목영문명', '대학대학원']:

        messages.error(request, '⚠️ 엑셀 내용이 다릅니다! 수정하지 않은 엑셀파일을 올려주세요.')
        return redirect('/mypage/')
    # 검사를 통과하면 df를 형식에 맞게 수정
    df.fillna('', inplace = True)

    # F 나 NP 과목은 삭제함
    for i, row in df.iterrows():
        if row['등급'] in ['F', 'FA', 'NP']:
            df.drop(i, inplace=True)
    # 불필요 컬럼 삭제
    df.drop(['담당교원', '등급', '삭제구분', '재수강구분', '공학인증', '공학요소', '공학세부요소', '인정구분', '성적인정대학명', '교과목영문명', '대학대학원'], axis=1, inplace=True)

    # 추가 전 user_grade DB에 이미 데이터가 있는지 확인 후 삭제
    user_id = request.session.get('id')
    ui_row = UserInfo.objects.get(student_id = user_id)
    ug = UserLecture.objects.filter(student_id = user_id)
    if ug.exists() : ug.delete()

    # DF를 테이블에 추가
    for i, row in df.iterrows():
        # 저장
        new_ug = UserLecture()
        new_ug.student_id = user_id
        new_ug.major = ui_row.major
        new_ug.year = row['년도']
        new_ug.semester = str(row['학기'])
        new_ug.subject_num = str(row['학수강좌번호'])
        new_ug.subject_name = row['교과목명']
        new_ug.classification = row['이수구분']
        new_ug.classification_ge = row['이수구분영역']
        new_ug.subject_credit = row['학점']
        new_ug.eng = row['원어강의종류']
        new_ug.save()
    # json DB도 업데이트
    update_json(user_id)
    messages.success(request, '업데이트성공')
    
    return redirect('/mypage/')
