from django.shortcuts import render
from django.contrib.auth import login

def user_login(request):
    # 로그인 처리 로직 작성
    if request.method == 'POST':
        # POST 요청으로부터 사용자 입력을 처리하고 로그인 처리를 수행합니다.
        # 예를 들어, 폼 검증 및 로그인 로직을 여기에 추가하세요.
        pass

    return render(request, "main/login.html")

# Create your views here.
def index(request):
    return render(request, "main/index.html")

