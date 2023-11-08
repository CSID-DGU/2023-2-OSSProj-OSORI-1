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
    grade_list = request.POST.getlist('grade[]') # 학점 
    selection_list = request.POST.getlist('selection[]') # 선택영역 
    
    # 선택영역 동국대 강의형식으로 수정완료
    if "공교" in selection_list:
        selection += ["자아성찰","대학탐구","시민","글쓰기","명작","리더십","지역연구","영어","한국문화","SW"]
    if "일교" in selection_list:
        selection += ["인문","사회","자연","문화예술체육","자기계발","융복합"]
    if "학기" in selection_list:
        selection += ["제4영역:자연과학","제5영역:외국어"]    
    
    # 에브리타임 강좌 목록에서 긁어올 정보
    cs_queryset = Lecture.objects.filter(
        classification = ['공교', '일교', '학기'], 
        classification_ge = selection, 
        grade__in= grade_list
    )
    cs_count = cs_queryset.values_list('sum_stu').annotate(count=Count('sum_stu'))
    # 쿼리셋을 리스트로 변환 -> 에브리타임 담은 강좌인원에 따라 내림차순 정렬 
    
    cs_count = sorted(list(cs_count), key = lambda x : x[1], reverse=True)
    zip_lecture_count = []
    for s_num, count in cs_count:
        if count < 10:
            continue
        al_queryset = Lecture.objects.filter(
            subject_num = s_num, 
            subject_name = s_name,
            classification = ['공교','학기','일교'], # 꿀교양찾기 페이지이기 때문에 교양만 추출 
            professor =pro,
            subject_credit = sub_c,
            classification_ge =selection_list
            grade__in=grade_list
        )
        if al_queryset.exists():
            lec_info = list(al_queryset.values())[0]
            zip_lecture_count.append([lec_info, count])
    # context 전송
    context={
        'zip_lecture_count': zip_lecture_count
    }
    return JsonResponse(context)