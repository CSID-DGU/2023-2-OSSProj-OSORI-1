# 장고 관련 참조
from django.http import JsonResponse
from django.core.serializers import serialize
from ..models import Lecture
# 모델 참조
from django.db.models import Count
from ..models import *
# AJAX 통신관련 참조
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def a_statistics_ge(request):
    # POST로 온 form 데이터 꺼내기
    grade_list = request.POST.getlist('grade[]') # 학점 
    selection_list = request.POST.getlist('selection[]') # 선택영역 
    
    # 선택영역 동국대 강의형식으로 수정완료
    selection =[]
    if "공통교양" in selection_list:
        selection += ["자아성찰","대학탐구","시민","글쓰기","명작","리더십","지역연구","영어","한국문화","SW"]
    if "일반교양" in selection_list:
        selection += ["인문","사회","자연","문화예술체육","자기계발","융복합"]
    if "학문기초" in selection_list:
        selection += ["제4영역:자연과학","제5영역:외국어"]    
    
    # 에브리타임 강좌 목록에서 긁어올 정보
    cs_queryset = Lecture.objects.filter(
        classification__in = ['공교', '일교', '학기'], 
        classification_ge__in = selection, 
        subject_credit__in = grade_list
    ).order_by('-sum_stu') # 에브리타임 담은 강좌인원에 따라 내림차순 정렬 

    zip_lecture_count = []
    if cs_queryset.exists():
            lecture = list(cs_queryset.values())
            zip_lecture_count.extend([lecture])
    # context 전송
    context={
        'zip_lecture_count': zip_lecture_count
    }
    return JsonResponse(context)
    # zip_lecture_count = []
    # for lecture in cs_queryset:
        # 다른 필드에 관한 조건은 필요한 경우 추가할 것
        # zip_lecture_count.append(lecture)

    # context 전송
    # context = {
    #     'zip_lecture_count': zip_lecture_count
    # }
    # return JsonResponse(context)

    # serialized_data = serialize('json', cs_queryset)
    # return JsonResponse({'serialized_data': serialized_data})