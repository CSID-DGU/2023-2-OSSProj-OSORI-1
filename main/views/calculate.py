# 파이썬 라이브러리
import json
import random
from collections import defaultdict
from django_pandas.io import read_frame
# 모델 참조
from django.db.models import Count
from ..models import *

def to_zip_list(list_1, list_2):
    zip_list = []
    for a, b in zip(list_1, list_2):
        zip_list.append([a,b])
    return zip_list

def list_to_query(list_):
    al = Lecture.objects.filter(subject_num__in=list_)
    return list(al.values())

def make_dic(my_list):
    my_list.sort()
    dic = defaultdict(lambda:-1)
    for s_num in my_list:
        dic[s_num]
        # 필수과목의 동일과목은 sg 테이블에서 1:1로만 담겨잇어야함.
        sg = SubjectGroup.objects.filter(subject_num = s_num)
        if sg.exists():
            dic[s_num] = sg[0].group_num
    return dic

def make_recommend_list(my_dic, dic):
    my_dic_ = my_dic.copy()
    dic_ = dic.copy()
    check = dic.copy()
    for k in check.keys():
        check[k] = 0
    # 만족한 학수번호는 딕셔너리에서 pop
    for s_num in my_dic_.keys():
        # 1차로 학수번호 검사
        # 있다면? -> 기준 딕셔너리에서 팝.
        if s_num in dic_.keys():
            check[s_num] = 1
            dic_.pop(s_num)
        # 없다면? 2차 검사 (사용자가 새 과목으로 재수강했을 경우)
        else :
            # 내 과목 리스트에서 그룹번호를 꺼냄
            g_num = my_dic_[s_num]
            # 기준 과목 리스트에서 그룹번호가 같은게 있으면 학수를 동일과목으로 바꿈
            for k, v in dic_.items():
                if v == g_num :
                    s_num = k
            # 해당 그룹번호가 기준에도 있다면 
            if g_num != -1 and (g_num in dic_.values()):
                check[s_num] = 1
                dic_.pop(s_num)
    # 추천 리스트 알고리즘
    recommend = []
    for s_num in dic_.keys():
        nl = NewLecture.objects.filter(subject_num = s_num)
        # 부족 과목이 열리고 있다면
        if nl.exists():
            recommend.append(nl[0].subject_num)
        # 더이상 열리지 않는다면 -> 그룹번호로 동일과목 찾은 후 열리는 것만 저장
        else:
            g_num = dic_[s_num]
            # 동일과목도 없고 과목이 없어졌다?
            if g_num == -1:
                recommend.append(s_num)
            # 아니면 동일과목중 열리고 있는 강의를 찾자
            else:
                sg = SubjectGroup.objects.filter(group_num = g_num)
                for s in sg:
                    nl2 = NewLecture.objects.filter(subject_num = s.subject_num)
                    if nl2.exists():
                        recommend.append(nl2[0].subject_num)
    return recommend, list(check.values())

def add_same_lecture(list_):
    for s_num in list_:
        sg = SubjectGroup.objects.filter(subject_num = s_num)
        for s in sg:
            rows = SubjectGroup.objects.filter(group_num = s.group_num)
            for r in rows:
                if r.subject_num not in list_:
                    list_.append(r.subject_num)
    return list_

def make_recommend_list_other(other_, user_lec_list):
    # 쿼리셋을 리스트로 변환 -> 등장횟수에 따라 내림차순 정렬 
    other_ = sorted(list(other_), key = lambda x : x[1], reverse=True)
    # 10개만 추천하기 + 내가 들었던 과목은 제외하기
    recom = []
    rank = 0
    for s_num, num in other_:
        if len(recom) >= 10:
            break
        # 뉴렉쳐에 있는 최신 학수번호 + 내가 안들은것만 담기 + 과목정보 - 등장횟수 순위 묶어서 저장
        if NewLecture.objects.filter(subject_num=s_num).exists() and (s_num not in user_lec_list):
            # AllLecture에서 이수구분이 맞을때만 리스트에 추가함
            al_qs = Lecture.objects.filter(subject_num = s_num, classification__in = ['전필', '전공', '공교', '학기'])
            if al_qs.exists():
                rank += 1
                row_dic = list(al_qs.values())
                recom.append( [row_dic[0], rank] )
    # 학수번호 -> 쿼리셋 -> 모든 정보 리스트로 변환 후 리턴
    return recom

def convert_to_int(num):
    if str(num)[-1] == '0':
        num = int(num)
    return num

def convert_selection(selection):
    if selection == "융합과창업":
        return "자기계발과진로"
    return selection

# ---------------------------------------------------- (졸업요건 검사 파트) ----------------------------------------------------------------

def f_result(user_id):
    # userinfo 테이블에서 행 추출
    ui_row = UserInfo.objects.get(student_id = user_id)
    # user_grade 테이블에서 사용자의 성적표를 DF로 변환하기
    user_qs = UserLecture.objects.filter(student_id = user_id)
    data = read_frame(user_qs, fieldnames=['subject_num', 'subject_name', 'classification', 'classification_ge', 'subject_credit'])
    data.rename(columns = {'subject_num' : '학수번호', 'subject_name' : '교과목명', 'classification' : '이수구분', 'classification_ge' : '이수구분영역', 'subject_credit' : '학점'}, inplace = True)
    # 사용자에게 맞는 기준 row 뽑아내기
    standard_row = Standard.objects.get(user_dep = ui_row.major, user_year = ui_row.student_id[2:3])

    # 아래 로직을 거치며 채워질 데이터바인딩용 context 선언
    result_context = {}

    ####################################################
    ################### 예외처리 여부 ###################
    ####################################################
    # 공교, 학기(외국어), 학기(msc), 복수, 영어 여부 판단
    ce_exists, lang_exists, msc_exists, multi_exists, english_exists = 0, 0, 0, 0, 0
    if standard_row.core_essential:
        ce_exists = 1
    if standard_row.basic_language:
        lang_exists = 1
    if standard_row.msc:
        msc_exists = 1
    if ui_row.major_status != '해당없음':
        multi_exists = 1 
    if json.loads(standard_row.english):
        english_exists = 1
    context_exists = {
        'ce' : ce_exists,
        'language' : lang_exists,
        'msc' : msc_exists,
        'english' : english_exists,
        'multi' : multi_exists,
    }
    result_context['exists'] = context_exists
        

    ###################################################
    ################### 사용자 정보 ###################
    ###################################################
    context_user_info = {
        'id' : ui_row.student_id,
        'name' : ui_row.name,
        'major' : ui_row.major,
        'year' : ui_row.student_id[2:3],
    }
    result_context['user_info'] = context_user_info

    ################################################
    ################### 전공 공통 ###################
    ################################################
    # 사용자의 성적표에서 전필, 전공 추출
    df_me = data[data['이수구분'].isin(['전필'])]
    df_me.reset_index(inplace=True,drop=True)
    df_ms = data[data['이수구분'].isin(['전공'])]
    df_ms.reset_index(inplace=True,drop=True)
    # 전필 기준에서 초과된 학점 계산
    remain = 0
    if standard_row.major_essential < df_me['학점'].sum() :
        remain = df_me['학점'].sum() - standard_row.major_essential
    # 내가들은 전필 + 전공의 동일과목 학수번호 추가한 리스트
    user_major_lec = add_same_lecture(df_ms['학수번호'].tolist() + df_me['학수번호'].tolist())

    ################################################
    ################### 전필 영역 ###################
    ################################################
    # 기준학점 & 사용자 학점 추출
    standard_num_me = standard_row.major_essential
    user_num_me = df_me['학점'].sum() - remain
    lack_me = standard_num_me - user_num_me
    # 선택추천과목 리스트 생성
    other_me = UserLecture.objects.exclude(year = '커스텀').filter(major = ui_row.major, classification = '전필').values_list('subject_num').annotate(count=Count('subject_num'))
    recom_selection_me = make_recommend_list_other(other_me, user_major_lec)
    # 패스여부 검사
    pass_me = 0
    if standard_num_me <= user_num_me:
        pass_me = 1
    # context 생성
    context_major_essential = {
        'standard_num' : standard_num_me,
        'user_num' : convert_to_int(user_num_me),
        'lack' : convert_to_int(lack_me),
        'recom_selection' : recom_selection_me,
        'pass' : pass_me,
    }
    result_context['major_essential'] = context_major_essential


    ################################################
    ################### 전공(전선) 영역 ###################
    ################################################
    # 기준학점 & 사용자학점합계 추출
    standard_num_ms = standard_row.major_selection
    user_num_ms = df_ms['학점'].sum()
    lack_ms = standard_num_ms - user_num_ms - remain
    # 선택추천과목 리스트 생성
    other_ms = UserLecture.objects.exclude(year = '커스텀').filter(major = ui_row.major, classification = '전공').values_list('subject_num').annotate(count=Count('subject_num'))
    recom_selection_ms = make_recommend_list_other(other_ms, user_major_lec)
    # 패스여부 검사
    pass_ms = 0
    if standard_num_ms <= user_num_ms + remain:
        pass_ms = 1
    # context 생성
    context_major_selection = {
        'standard_num' : standard_num_ms,
        'user_num' : convert_to_int(user_num_ms),
        'remain' : convert_to_int(remain),
        'lack' : convert_to_int(lack_ms),
        'recom_selection' : recom_selection_ms,
        'pass' : pass_ms,
    }
    result_context['major_selection'] = context_major_selection


    ################################################
    ################### 공교 영역 ###################
    ################################################
    if ce_exists :
        # 기준필수과목 & 사용자교필과목 추출 => 동일과목 매핑 dict 생성
        dic_ce = make_dic([s_num for s_num in standard_row.ce_list.split('/')])
        user_dic_ce = make_dic(data['학수번호'].tolist())  # * 수정 : 교필, 중필 영역만 비교하지 않고 전체를 대상으로 비교
        # 기준필수과목+체크 & 추천과목 리스트 생성
        recom_essential_ce, check_ce = make_recommend_list(user_dic_ce, dic_ce)
        standard_essential_ce = to_zip_list(list_to_query(dic_ce.keys()), check_ce)
        # 필수과목, 이수과목 개수 저장
        standard_num_ce = len(dic_ce)
        user_num_ce = sum(check_ce)
        # 패스여부 검사
        pass_ce = 0
        if standard_num_ce == user_num_ce :
            pass_ce = 1
        # context 생성
        context_core_essential = {
            'standard_num' : standard_num_ce,
            'user_num' : convert_to_int(user_num_ce),
            'recom_essential' : list_to_query(recom_essential_ce),
            'standard_essential' : standard_essential_ce,
            'pass' : pass_ce,
        }
        result_context['core_essential'] = context_core_essential


    ################################################
    ################### 학기(외국어) 영역 ###################
    ################################################
    if lang_exists :
        # 성적표에서 학기 추출
        df_cs = data[data['이수구분'].isin(['학기'])]
        df_cs.reset_index(inplace=True,drop=True)
        # 기준학점 & 사용자학점합계 추출
        standard_num_cs = standard_row.basic_language
        user_num_cs = df_cs['학점'].sum()
        # 기준필수과목 & 사용자과목 추출 => 동일과목 매핑 dict 생성
        dic_cs = make_dic([s_num for s_num in standard_row.cs_list.split('/')])
        user_dic_cs = make_dic(data['학수번호'].tolist())    # * 수정 : 필수과목은 교선1만 검사하지 않고 모든 학수번호를 대상으로 검사 
        # 기준필수과목+체크 & 추천과목 리스트 생성
        recom_essential_cs, check_cs = make_recommend_list(user_dic_cs, dic_cs)
        standard_essential_cs = to_zip_list(list_to_query(dic_cs.keys()), check_cs)
        
        # 선택영역 검사
        standard_cs_part =["사상과역사","사회와문화","자연과과학기술","세계와지구촌","예술과체육","자기계발과진로"]   # 기준 영역 6개
        # 융합과창업 -> 자기계발과진로 변경
        df_cs["선택영역"] = df_cs["선택영역"].apply(convert_selection)
        user_cs_part = list(set(df_cs[df_cs['선택영역'].isin(standard_cs_part)]['선택영역'].tolist()))
        # 사용자가 안들은 영역 추출
        recom_cs_part = []
        if len(user_cs_part) < 3:
            recom_cs_part = list(set(standard_cs_part) - set(user_cs_part))
        # 사용자의 부족 영역 체크
        part_check = ['이수' for _ in range(len(standard_cs_part))]
        for i, c in enumerate(standard_cs_part):
            if c not in user_cs_part:
                part_check[i] = '미이수'

        # 선택추천과목 리스트 생성
        if not recom_cs_part :  # 만족한경우엔 5개 다 추천
            cs_part_for_recom = standard_cs_part
        else:                   # 만족 못했으면 영역 recom 리스트 그대로
            cs_part_for_recom = recom_cs_part
        other_cs = UserGrade.objects.exclude(year = '커스텀').filter(classification__in = ['교선1', '중선'],  selection__in=cs_part_for_recom)
        other_cs = other_cs.values_list('subject_num').annotate(count=Count('subject_num'))
        user_cs_lec = df_cs['학수번호'].tolist() + [s_num for s_num in standard_row.cs_list.split('/')]
        recom_selection_cs = make_recommend_list_other(other_cs, user_cs_lec)
        # 패스여부 검사 (선택영역, 기준학점, 필수과목, 전체)
        pass_cs_part, pass_cs_num, pass_cs_ess, pass_cs= 0, 0, 0, 0
        if not recom_cs_part:
            pass_cs_part = 1
        if standard_num_cs <= user_num_cs:
            pass_cs_num = 1
        if not recom_essential_cs:
            pass_cs_ess = 1
        if pass_cs_part and pass_cs_num and pass_cs_ess:
            pass_cs = 1

        # context 생성
        context_core_selection = {
            'standard_num' : standard_num_cs,
            'user_num' : convert_to_int(user_num_cs),
            'recom_essential' : list_to_query(recom_essential_cs),
            'standard_essential' : standard_essential_cs,
            'recom_selection' : recom_selection_cs,
            'standard_cs_part' : standard_cs_part,
            'part_check' : part_check,
            'pass_part' : pass_cs_part,
            'pass_ess' : pass_cs_ess,
            'pass' : pass_cs,
        }
        result_context['core_selection'] = context_core_selection

    
    ################################################
    ################### 균필 영역 ###################
    ################################################
    if la_balance_exists :
        # 성적표에서 균필 과목 추출
        df_la_balance = data[data['이수구분'].isin(['균필'])]
        df_la_balance.reset_index(inplace=True,drop=True)

        # 기준학점 & 사용자학점합계 추출
        standard_num_la_balance = standard_row.la_balance
        user_num_la_balance = df_la_balance['학점'].sum()

        # 허용영역 기준 생성 -> 대학별 영역 제외
        standard_la_balance_part = ["역사와사상", "자연과과학", "경제와사회", "문화와예술"]
        if user_major_row.college in ["인문과학대학"]:
            standard_la_balance_part.remove("역사와사상")
        elif user_major_row.college in ["자연과학대학", "생명과학대학", "전자정보공학대학", "소프트웨어융합대학", "공과대학"]:
            standard_la_balance_part.remove("자연과과학")
        elif user_major_row.college in ["사회과학대학", "경영경제대학", "호텔관광대학"]:
            standard_la_balance_part.remove("경제와사회")
        elif user_major_row.college in ["예체능대학"]:
            standard_la_balance_part.remove("문화와예술")
        # 디이베/만애텍은 예체능으로 침
        if ui_row.major in ["디자인이노베이션전공", "만화애니메이션텍전공"]:
            standard_la_balance_part = ["역사와사상", "자연과과학", "경제와사회"]

        # 사용자가 들은 선택영역 추출
        user_la_balance_part = list(set(df_la_balance[df_la_balance['선택영역'].isin(standard_la_balance_part)]['선택영역'].tolist()))
        # 사용자가 안들은 영역 추출
        lack_la_balance_part = []
        if len(user_la_balance_part) < 2:   # 기준영역 - 사용자들은영역 = 부족영역
            lack_la_balance_part = list(set(standard_la_balance_part) - set(user_la_balance_part))
        # 사용자의 부족 영역 체크
        check_la_balance_part = ['이수' for _ in range(len(standard_la_balance_part))]
        for i, c in enumerate(standard_la_balance_part):
            if c not in user_la_balance_part:
                check_la_balance_part[i] = '미이수'

        # 과목 추천리스트 생성 -> 부족영역이 있을때만 생성
        recom_la_balance = []
        if lack_la_balance_part:
            al_qs = AllLecture.objects.filter(
                classification = '균필', 
                selection__in = lack_la_balance_part,
            )
            recom_la_balance = list(al_qs.values())

        # 패스여부 검사 (선택영역, 기준학점, 전체)
        pass_la_balance_part, pass_la_balance_num, pass_la_balance= 0, 0, 0
        if not lack_la_balance_part:
            pass_la_balance_part = 1
        if standard_num_la_balance <= user_num_la_balance:
            pass_la_balance_num = 1
        if pass_la_balance_part and pass_la_balance_num:
            pass_la_balance = 1
        
        # context 생성
        context_la_balance = {
            'standard_num' : standard_num_la_balance,
            'user_num' : convert_to_int(user_num_la_balance),
            'recom' : recom_la_balance,
            'standard_part' : standard_la_balance_part,
            'part_check' : check_la_balance_part,
            'pass_part' : pass_la_balance_part,
            'pass' : pass_la_balance,
        }
        result_context['la_balance'] = context_la_balance


    ################################################
    ################### 기교/기필 영역 ###################
    ################################################
    if b_exists :
        # 기준필수과목 & 사용자교필과목 추출 => 동일과목 매핑 dict 생성
        dic_b = make_dic([s_num for s_num in standard_row.b_list.split('/')])
        user_dic_b = make_dic(data['학수번호'].tolist())     # * 수정 : 기교 영역만 비교하지 않고 전체를 대상으로 비교
        # 기준필수과목+체크 & 추천과목 리스트 생성
        recom_essential_b, check_b = make_recommend_list(user_dic_b, dic_b)
        standard_essential_b = to_zip_list(list_to_query(dic_b.keys()), check_b)
        # 필수과목, 이수과목 개수 저장
        standard_num_b = len(dic_b)
        user_num_b = sum(check_b)
        # 패스여부 검사
        pass_b = 0
        if standard_num_b == user_num_b :
            pass_b = 1
        # context 생성
        context_basic = {
            'standard_num' : standard_num_b,
            'user_num' : convert_to_int(user_num_b),
            'recom_essential' : list_to_query(recom_essential_b),
            'standard_essential' : standard_essential_b,
            'pass' : pass_b,
        }
        
        # 화학과 기교에서는 조건이 추가된다.
        if ui_row.major == '화학과':
            pass_chemy_all = pass_b
            chemy_B_exists = 0
            # 기교 -> 선택과목 기준 설정
            if ui_row.year >= 19:
                data_chemy_A = ['2657', '3353']             # 일생 / 통계
                data_chemy_B = []
            elif ui_row.year >= 16:
                data_chemy_A = ['2647', '2657']             # 일물실1 / 일생
                data_chemy_B = ['2649', '2657', '3353']     # 일물실2 / 일생 / 통계
            else:
                data_chemy_A = ['4082', '2647', '2657']     # 고미적1 / 일물실1 / 일생
                data_chemy_B = ['4300', '2649']             # 고미적 2 / 일물실2

            dic_chemy_A = make_dic(data_chemy_A)
            recom_chemy_A, check_chemy_A = make_recommend_list(user_dic_b, dic_chemy_A)
            standard_chemy_A = to_zip_list(list_to_query(dic_chemy_A.keys()), check_chemy_A)
            pass_chemy_A = 0
            if 1 in check_chemy_A:
                pass_chemy_A = 1
            else:
                pass_chemy_all = 0
                context_basic['recom_chemy_A'] = list_to_query(recom_chemy_A)
            context_basic['standard_chemy_A'] = standard_chemy_A
            context_basic['pass_chemy_A'] = pass_chemy_A
                
            if data_chemy_B:
                chemy_B_exists = 1
                dic_chemy_B = make_dic(data_chemy_B)
                recom_chemy_B, check_chemy_B = make_recommend_list(user_dic_b, dic_chemy_B)
                standard_chemy_B = to_zip_list(list_to_query(dic_chemy_B.keys()), check_chemy_B)
                pass_chemy_B = 0
                if 1 in check_chemy_B:
                    pass_chemy_B = 1
                else:
                    pass_chemy_all = 0
                    context_basic['recom_chemy_B'] =list_to_query(recom_chemy_B)
                context_basic['standard_chemy_B'] = standard_chemy_B
                context_basic['pass_chemy_B'] = pass_chemy_B

            context_basic['chemy_B_exists'] = chemy_B_exists
            context_basic['pass_chemy_all'] = pass_chemy_all

        result_context['basic'] = context_basic


    ################################################
    ################### 영어 영역 ###################
    ################################################
    if english_exists:
        # 영어합격기준 (영문과만 예외처리)
        eng_standard = json.loads(standard_row.english)
        # 영어 인증 여부
        eng_pass, eng_score = 0, 0
        eng_category = ui_row.eng
        # 인텐시브 들었다면 통과
        if '6844' in data['학수번호'].tolist():
            eng_category = 'Intensive English 이수'
            eng_pass = 1
        else:
            if eng_category != '해당없음':
                if eng_category == '초과학기면제': 
                    eng_pass = 1
                # 영어 점수 기재했을 경우
                else: 
                    eng_category, eng_score = eng_category.split('/')
                    # # OPIc일 경우
                    # if eng_category == 'OPIc':
                    #     # 영어영문은 기준이 더 높다
                    #     if ui_row.major == '영어영문학전공':
                    #         opic_standard = ['AL', 'IH', 'IM']
                    #     else:
                    #         opic_standard = ['AL', 'IH', 'IM', 'IL']
                    #     if eng_score in opic_standard:
                    #         eng_pass = 1
                    # elif int(eng_score) >= eng_standard[eng_category] :
                    #     eng_pass = 1
        context_english = {
            'standard' : eng_standard,
            'category' : eng_category,
            'score' : eng_score,
            'pass' : eng_pass,
        }
        result_context['english'] = context_english


    #####################################################
    ################### 복수/연계 전공 ###################
    #####################################################
    # 복수/연계 전공시 -> 전필,전선 : 기준 수정 + 복필(연필),복선(연선) : 기준과 내 학점계산 추가
    if multi_exists:
        result_context['user_info']['major_status'] = ui_row.major_status
        # 복수/연계 전공 이수구분 + 기준학점 설정
        new_standard_me = 15
        new_standard_ms = 24
        standard_multi_me = 15
        standard_multi_ms = 24
        if ui_row.major_status == '복수전공':
            classification_me = '복필'
            classification_ms = '복선'
        elif ui_row.major_status == '연계전공':
            classification_me = '연필'
            classification_ms = '연선'
        # 전공 기준 학점 수정
        result_context['major_essential']['standard_num'] = new_standard_me
        result_context['major_selection']['standard_num'] = new_standard_ms
        # 전필 -> 전선 넘기기 연산 다시하기
        remain = 0
        if new_standard_me < df_me['학점'].sum() :
            remain = df_me['학점'].sum() - new_standard_me
        result_context['major_essential']['user_num'] = convert_to_int(df_me['학점'].sum() - remain)
        result_context['major_selection']['remain'] = convert_to_int(remain)
        result_context['major_selection']['user_num'] = convert_to_int(user_num_ms)
        # 전공 패스여부 다시 검사
        pass_me, pass_ms = 0,0
        if new_standard_me <= user_num_me: 
            pass_me = 1
        if new_standard_ms <= user_num_ms + remain: 
            pass_ms = 1
        result_context['major_essential']['pass'] = pass_me
        result_context['major_selection']['pass'] = pass_ms
        # 전공 부족학점 다시 계산
        result_context['major_essential']['lack'] = convert_to_int(new_standard_me - user_num_me)
        result_context['major_selection']['lack'] = convert_to_int(new_standard_ms - user_num_ms - remain)
        # 각각 X필, X선 학점 계산
        user_multi_me = data[data['이수구분'].isin([classification_me])]['학점'].sum()
        multi_remain = 0    # X필 초과시 X선으로 넘어가는 학점
        if standard_multi_me < user_multi_me :
            multi_remain = user_multi_me - standard_multi_me
        user_multi_me -= multi_remain
        user_multi_ms = data[data['이수구분'].isin([classification_ms])]['학점'].sum()
        # 복수/연계전공 pass 여부 검사
        pass_multi_me, pass_multi_ms = 0, 0
        if standard_multi_me <= user_multi_me:
            pass_multi_me = 1
        if standard_multi_ms <= user_multi_ms + multi_remain:
            pass_multi_ms = 1
        # 복수/연계 전공 context 생성
        context_multi_major_essential = {
            'standard_num' : standard_multi_me,
            'user_num' : convert_to_int(user_multi_me),
            'pass' : pass_multi_me,
        }
        context_multi_major_selection = {
            'standard_num' : standard_multi_ms,
            'user_num' : convert_to_int(user_multi_ms),
            'remain' : convert_to_int(multi_remain),
            'pass' : pass_multi_ms,
        }
        result_context['multi_major_essential'] = context_multi_major_essential
        result_context['multi_major_selection'] = context_multi_major_selection


    #############################################
    ################### Total ###################
    #############################################
    standard_num_total = standard_row.sum_score
    user_num_total = data['학점'].sum()
    # 총 기준 학점 넘기 + 모든 영역에서 pass 받으면 통과
    pass_total = 1
    if standard_num_total > user_num_total:
        pass_total = 0
    else:
        for key in result_context:
            try:
                if not result_context[key]['pass'] :
                    pass_total = 0
                    break
            except:
                pass
    # 화학과는 한번더 검사
    if ui_row.major == '화학과':
        if not result_context['basic']['pass_chemy_all']:
            pass_total = 0

    context_total = {
        'standard_num' : standard_num_total,
        'user_num' : convert_to_int(user_num_total),
        'pass' : pass_total,
    }
    result_context['total'] = context_total

    return result_context

    # @@@ result_context 구조 @@@
    # result_context = {
    #     'exists',
    #     'user_info',
    #     'book',
    #     'english',
    #     'major_essential',
    #     'major_selection',
    #     'core_essential',
    #     'core_selection',
    #     'basic',
    #     'multi_major_essential',
    #     'multi_major_selection',
    #     'total',
    # }