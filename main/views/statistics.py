# 장고 관련 참조
from django.http import JsonResponse
# 모델 참조
from django.db.models import Count
from ..models import *
# AJAX 통신관련 참조
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def a_statistics(request):
    # POST로 온 form 데이터 꺼내기
    grade_list = request.POST.getlist('grade[]')
    selection_list = request.POST.getlist('selection[]')

    # 선택영역 동국대 강의형식으로 나중에 추가로 수정 예정
    if "통계학과" in selection_list:
        selection_list += Lecture.objects.filter(subject_num__startswith ='STA').values_list('subject_num', flat=True)
    if "행정학과" in selection_list:
        selection_list += Lecture.objects.filter(subject_num__startswith ='PUB').values_list('subject_num', flat=True)
    if "산업시스템공학과" in selection_list:
         selection_list += Lecture.objects.filter(subject_num__startswith ='ISE').values_list('subject_num', flat=True)
    if "융합소프트웨어학과" in selection_list:
        selection_list += Lecture.objects.filter(subject_num__startswith ='SCS').values_list('subject_num', flat=True)
    
    # 사용자 과목정보에서 긁어올 정보 수정예정
    cs_queryset = Lecture.objects.filter(
        classification = '전공', 
        subject_num__in = selection_list, 
        subject_credit__in = grade_list
    ).order_by('-sum_stu')

    zip_lecture_count = []
    if cs_queryset.exists():
            lecture = list(cs_queryset.values())
            # zip_lecture_count.append([lecture])
    else:
         lecture =[]
    # context 전송
    context={
        # 'zip_lecture_count': zip_lecture_count
        'zip_lecture_count' : lecture
    }
    return JsonResponse(context)