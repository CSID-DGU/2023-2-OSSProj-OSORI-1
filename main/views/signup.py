# 파이썬 라이브러리
import bcrypt
# 장고 관련 참조
from django.shortcuts import redirect
# 모델 참조
from ..models import *
# AJAX 통신관련 참조
from django.views.decorators.csrf import csrf_exempt


def f_register(request):
    name = request.POST.get('name')
    major = request.POST.get('major')
    student_id = request.POST.get('student_id')
    email = request.POST.get('email')

    # 비밀번호를 DB에 저장하기 전 암호화
    password = request.POST.get('password')
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    # 인코딩 + 솔팅 + 해싱 -> 암호화
    password = password.decode('utf-8')                                     # 저장전 디코딩

    # 만약 영어 점수 썼다면 ex) 'toeic/550' <- 이런형태로 저장됨.
    eng = request.POST.get('eng')
    if eng not in ['해당없음', '초과학기면제', '영어인증면제학과']:
        eng = eng + '/' + str(request.POST.get('eng_score'))

    # 졸업논문 통과여부
    thesis = request.POST.get('thesis_status')

    # 테스트 user_info 테이블에 데이터 입력
    new_ui = UserInfo()
    new_ui.student_id = student_id
    new_ui.password = password
    new_ui.major = major
    new_ui.name = name
    new_ui.thesis = thesis
    new_ui.eng = eng
    new_ui.email = email
    new_ui.save()

    return redirect('/success/')