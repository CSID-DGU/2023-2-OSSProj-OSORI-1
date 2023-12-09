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
    return dic

def check_list(my_dic, dic):
    my_dic_ = my_dic.copy()
    dic_ = dic.copy()
    check = dic.copy()
    for k in check.keys():
        check[k] = 0
    # 만족한 학수강좌번호는 딕셔너리에서 pop
    for s_num in my_dic_.keys():
        # 1차로 학수강좌번호 검사
        # 있다면? -> 기준 딕셔너리에서 팝.
        if s_num in dic_.keys():
            check[s_num] = 1
            dic_.pop(s_num)
    return list(check.values())

def convert_to_int(num):
    if str(num)[-1] == '0':
        num = int(num)
    return num

# ---------------------------------------------------- (졸업요건 검사 파트) ----------------------------------------------------------------

def f_result(user_id):
    # userinfo 테이블에서 행 추출
    ui_row = UserInfo.objects.get(student_id = user_id)
    # user_grade 테이블에서 사용자의 성적표를 DF로 변환하기
    user_qs = UserLecture.objects.filter(student_id = user_id)
    data = read_frame(user_qs, fieldnames=['subject_num', 'subject_name', 'classification', 'classification_ge', 'subject_credit', 'eng'])
    data.rename(columns = {'subject_num' : '학수강좌번호', 'subject_name' : '교과목명', 'classification' : '이수구분', 'classification_ge' : '이수구분영역', 'subject_credit' : '학점', 'eng' : '영어강의'}, inplace = True)
    # 사용자에게 맞는 기준 row 뽑아내기
    standard_row = Standard.objects.get(major = ui_row.major, year = ui_row.student_id[2:4])
    # 사용자 dictionary (필수과목 체크용)
    user_dic = make_dic(data['학수강좌번호'].tolist())

    # 아래 로직을 거치며 채워질 데이터바인딩용 context 선언
    result_context = {}

    ####################################################
    ################### 예외처리 여부 ###################
    ####################################################
    # 학기(5영역:외국어), 학기(4영역:자연과학), 복수, 영어 여부 판단
    major_ess_exists, basic_eng_exists, basic_exists, multi_exists = 0, 0, 0, 0
    if standard_row.major_essential:
        major_ess_exists = 1
    if standard_row.basic_eng:
        basic_eng_exists = 1
    if standard_row.basic:
        basic_exists = 1
    if ui_row.major_state != '해당없음':
        multi_exists = 1 
    context_exists = {
        'major_ess' : major_ess_exists,
        'basic_eng' : basic_eng_exists,
        'basic' : basic_exists,
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
        'year' : ui_row.student_id[2:4],
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
        
    df_me_eng = df_me[df_me['영어강의'].isin(['영어'])]
    df_ms_eng = df_ms[df_ms['영어강의'].isin(['영어'])]
    major_eng = df_me_eng['학점'].sum() + df_ms_eng['학점'].sum()

    ################################################
    ################### 전필 영역 ###################
    ################################################
    if major_ess_exists:
        # 기준학점 & 사용자 학점 추출
        standard_num_me = standard_row.major_essential
        user_num_me = df_me['학점'].sum()
        lack_me = standard_num_me - user_num_me
    
        # 패스여부 검사
        pass_me = 0
        if standard_num_me <= user_num_me:
            pass_me = 1
        # context 생성
        context_major_essential = {
            'standard_num' : standard_num_me,
            'user_num' : convert_to_int(user_num_me),
            'lack' : convert_to_int(lack_me),
            'pass' : pass_me,
        }
        result_context['major_essential'] = context_major_essential


    ################################################
    ################ 전공(전선) 영역 ################
    ################################################
    # 기준학점 & 사용자학점합계 추출
    standard_num_ms = standard_row.major_credit - standard_row.major_essential
    user_num_ms = df_ms['학점'].sum()
    lack_ms = standard_num_ms - user_num_ms
    
    if standard_row.major_selection_list:
        pass_ms_essential = 0
        pass_sel_ess = 1
        dic_selection = make_dic([s_num for s_num in standard_row.major_selection_list.split('/')])
        # 기준필수과목+체크
        check_selection = check_list(user_dic, dic_selection)
        if 0 not in check_selection:
            pass_ms_essential = 1
        standard_essential_selection = to_zip_list(list_to_query(dic_selection.keys()), check_selection)
    else:
        pass_ms_essential = 1
        pass_sel_ess = 0
        standard_essential_selection = ['해당없음']
        
    if standard_row.eng_major <= major_eng:
        major_eng_ess = ["이수"]
    else:
        major_eng_ess = ["미이수"]
        
    # 패스여부 검사
    pass_ms, pass_sel = 0, 0
    if standard_num_ms <= user_num_ms:
        pass_ms = 1
    if pass_ms and pass_ms_essential:
        pass_sel = 1
        
    # context 생성
    context_major_selection = {
        'standard_num' : standard_num_ms,
        'user_num' : convert_to_int(user_num_ms),
        'pass_ess' : pass_sel_ess,
        'standard_essential' : standard_essential_selection,
        'english_essential' : major_eng_ess,
        'lack' : convert_to_int(lack_ms),
        'pass' : pass_sel,
    }
    result_context['major_selection'] = context_major_selection
    

    ################################################
    ################### 공교 영역 ###################
    ################################################
    # explore, self, civ, writing, seminar, leader, eas, sw
    df_common = data[data['이수구분'].isin(['공교'])]
    df_common.reset_index(inplace=True,drop=True)
    
    standard_num_common = standard_row.common
    user_num_common = df_common['학점'].sum()
    
    # 선택영역 검사
    standard_common_part =["대학생활탐구","자아성찰", "리더십", "전지구적사고와과제","글쓰기","영어","세계명작세미나", "소프트웨어"]  
    # 사용자의 부족 영역 체크
    part_check = ['이수' for _ in range(len(standard_common_part))]
    
    if standard_row.explore > 0:
        df_exp = data[data['이수구분영역'].isin(['대학탐구'])]
        if standard_row.explore > df_exp['학점'].sum():
            part_check[0] = '미이수'
    else:
        part_check[0] = '해당없음'
            
    if standard_row.self > 0:
        df_self = data[data['이수구분영역'].isin(['자아성찰'])]
        if standard_row.self > df_self['학점'].sum():
            part_check[1] = '미이수'
    else:
        part_check[1] = '해당없음'
            
    if standard_row.civ > 0:
        df_lead = data[data['이수구분영역'].isin(['리더십'])]
        if standard_row.leader > df_lead['학점'].sum():
            part_check[2] = '미이수'
    else:
        part_check[2] = '해당없음'
        
    if standard_row.civ > 0:
        df_civ = data[data['이수구분영역'].isin(['지역연구', '시민', '미래위험사회와 안전'])]
        if standard_row.civ > df_civ['학점'].sum():
            part_check[3] = '미이수'
    else:
        part_check[3] = '해당없음'
        
    if standard_row.writing > 0:
        df_write = data[data['이수구분영역'].isin(['글쓰기'])]
        if standard_row.writing > df_write['학점'].sum():
            part_check[4] = '미이수'
    else:
        part_check[4] = '해당없음'   
    
    eng_category, eng_score = ui_row.eng.split('/')
    if int(eng_score) < 900:
        df_eng = data[data['이수구분영역'].isin(['영어'])]
        if standard_row.eas > df_eng['학점'].sum():
            part_check[5] = '미이수'
    else:
        part_check[5] = '면제'
        
    if standard_row.seminar > 0:
        df_seminar = data[data['이수구분영역'].isin(['명작'])]
        if standard_row.seminar > df_seminar['학점'].sum():
            part_check[6] = '미이수'
    else:
        part_check[6] = '해당없음'
        
    if standard_row.sw > 0:
        df_sw = data[data['이수구분영역'].isin(['SW'])]
        if standard_row.sw > df_sw['학점'].sum():
            part_check[7] = '미이수'
    else:
        part_check[7] = '해당없음'
    
    # 패스여부 검사
    pass_common = 0
    if '미이수' not in part_check :
        pass_common = 1
    
    context_common = {
            'standard_num' : standard_num_common,
            'user_num' : convert_to_int(user_num_common),
            'standard_part' : standard_common_part,
            'part_check' : part_check,
            'pass' : pass_common,
        }
    result_context['common'] = context_common
        
    ################################################
    ############### 학기(자연과학) 영역 #############
    ################################################
    if basic_exists :
        df_basic = data[data['이수구분영역'].isin(['제4영역:자연과학'])]
        df_basic.reset_index(inplace=True,drop=True)
        # 기준학점 & 사용자학점합계 추출
        standard_num_basic = standard_row.basic
        user_num_basic = df_basic['학점'].sum()
        
        # 기준필수과목 & 사용자과목 추출 => 동일과목 매핑 dict 생성
        dic_basic = defaultdict(lambda:-1)
        basic_lists = [standard_row.basic_list_m, standard_row.basic_list_s, standard_row.basic_list_c]

        for basic_list in basic_lists:
            if basic_list:
                dic_basic.update(make_dic([s_num for s_num in basic_list.split('/')]))
        
        # 기준필수과목+체크
        check_basic = check_list(user_dic, dic_basic)
        standard_essential_basic = to_zip_list(list_to_query(dic_basic.keys()), check_basic)

        # 패스여부 검사 (이수구분영역, 기준학점, 필수과목, 전체)
        pass_basic_num, pass_basic_ess, pass_basic= 0, 0, 0
        if standard_num_basic <= user_num_basic:
            pass_basic_num = 1
        if 0 not in check_basic:
            pass_basic_ess = 1
        if pass_basic_num and pass_basic_ess:
            pass_basic = 1

        # context 생성
        context_basic = {
            'standard_num' : standard_num_basic,
            'user_num' : convert_to_int(user_num_basic),
            'standard_essential' : standard_essential_basic,
            'pass_ess' : pass_basic_ess,
            'pass' : pass_basic,
        }
        result_context['basic'] = context_basic
    
    
    ################################################
    ############## 학기(외국어) 영역 ################
    ################################################
    if basic_eng_exists :
        # 성적표에서 학기 추출
        df_basic_eng = data[data['이수구분영역'].isin(['제5영역:외국어'])]
        df_basic_eng.reset_index(inplace=True,drop=True)
        
        # 기준학점 & 사용자학점합계 추출
        standard_num_basic_eng = standard_row.basic_eng
        user_num_basic_eng = df_basic_eng['학점'].sum()
        
        # 패스여부 검사 (이수구분영역, 기준학점, 전체)
        pass_basic_eng = 0
        if standard_num_basic_eng <= user_num_basic_eng:
            pass_basic_eng = 1

        # context 생성
        context_basic_eng = {
            'standard_num' : standard_num_basic_eng,
            'user_num' : convert_to_int(user_num_basic_eng),
            'pass' : pass_basic_eng,
        }
        result_context['basic_eng'] = context_basic_eng
            
    
    #####################################################
    ################### 복수/연계 전공 ###################
    #####################################################
    # 복수/연계 전공시 -> 전필,전선 : 기준 수정 + 복필(연필),복선(연선) : 기준과 내 학점계산 추가
    if multi_exists:
        result_context['user_info']['major_state'] = ui_row.major_state
        multi_standard = Standard.objects.get(major = ui_row.sub_major)
        
        # 복수/연계 전공 이수구분 + 기준학점 설정
        new_standard = standard_row.s_credit - standard_row.major_essential
        standard_multi_me = multi_standard.major_essential
        standard_multi_ms = multi_standard.major_selection
        
        # 전공 기준 학점 수정
        result_context['major_selection']['standard_num'] = new_standard
        # 전필 -> 전선 넘기기 연산 다시하기
        result_context['major_selection']['user_num'] = convert_to_int(user_num_ms)
        
        # 전공 패스여부 다시 검사
        pass_ms = 0
        if new_standard <= user_num_ms: 
            pass_ms = 1
        result_context['major_selection']['pass'] = pass_ms
        
        # 전공 부족학점 다시 계산
        result_context['major_selection']['lack'] = convert_to_int(new_standard - user_num_ms)
        
        # 각각 X필, X선 학점 계산
        user_multi = data[data['이수구분'].isin(['복수1'])]['학점'].sum()
        
        dic_multi = make_dic([s_num for s_num in multi_standard.major_selection_list.split('/')])
        # 기준필수과목+체크
        check_multi = check_list(user_dic, dic_multi)
        standard_multi = to_zip_list(list_to_query(dic_multi.keys()), check_multi)
        user_multi_ms = user_multi - len(check_multi)
        
        # 복수/연계전공 pass 여부 검사
        pass_multi_me, pass_multi_ms = 0, 0
        if 0 not in check_multi:
            pass_multi_me = 1
        if standard_multi_ms <= user_multi_ms:
            pass_multi_ms = 1
            
        # 복수/연계 전공 context 생성
        context_multi_major_essential = {
            'standard_num' : standard_multi_me,
            'user_num' : len(check_multi),
            'standard_multi' : standard_multi,
            'pass' : pass_multi_me,
        }
        context_multi_major_selection = {
            'standard_num' : standard_multi_ms,
            'user_num' : convert_to_int(user_multi_ms),
            'pass' : pass_multi_ms,
        }
        result_context['multi_major_essential'] = context_multi_major_essential
        result_context['multi_major_selection'] = context_multi_major_selection


    #############################################
    ################### Total ###################
    #############################################
    standard_num_total = standard_row.total
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