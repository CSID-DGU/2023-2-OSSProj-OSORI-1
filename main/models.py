import os
from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# ------------------------------------- ( 회원 정보 테이블 ) -------------------------------------

password_validator = RegexValidator(
    regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
    message="비밀번호는 대문자, 소문자, 특수 문자 및 숫자를 포함해야 합니다."
)

class UserInfo(models.Model): 
    student_id = models.CharField(primary_key=True, max_length=10) # 학번 입력요구
    password = models.CharField(max_length=100, validators=[password_validator]) # 비밀번호
    major = models.CharField(max_length=45) # 전공
    sub_major = models.CharField(max_length=45, blank=True, null=True) # 부전공
    major_state = models.CharField(max_length=45) # 전공상태(복수,연계/융합,해당없음)
    name = models.CharField(max_length=45) # 학생 이름
    thesis = models.CharField(max_length=10) # 졸업논문(시험) 통과여부(o,x)
    eng = models.CharField(max_length=30) # 영어 공인 성적(토익기준)
    email = models.CharField(max_length=30) # 비밀번호 찾기 기능 때 필요
    mypage_json = models.JSONField(blank=True, null=True)
    result_json = models.JSONField(blank=True, null=True)
    en_result_json = models.JSONField(blank=True, null=True)

    class Meta:  # 자동 migrate 막을 때 사용
        managed = False
        db_table = 'main_userinfo'

# ------------------------------------- ( 강의 정보 테이블 ) -------------------------------------

class UserLecture(models.Model): # 학생성적정보파일 업로드 시 저장
    subject_num = models.CharField( max_length=10)
    subject_name = models.CharField(max_length=70)
    classification = models.CharField(max_length=45) # 전공과 교양 구분은 이 필드로
    classification_ge = models.CharField(max_length=45)
    professor = models.CharField(max_length=50)
    student_id = models.CharField(max_length=10)
    major = models.CharField(max_length=50)
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=20)
    subject_credit = models.FloatField()
    id = models.AutoField(primary_key=True)

    class Meta:
       managed = False
       db_table = 'main_userlecture'

class Lecture(models.Model): # 에브리타임 강의 크롤링
    subject_num = models.CharField(primary_key=True, max_length=10)
    subject_name = models.CharField(max_length=70)
    classification = models.CharField(max_length=45)
    classification_ge = models.CharField(max_length=45)
    professor = models.CharField(max_length=50)
    subject_credit = models.IntegerField()
    sum_stu = models.IntegerField() # 강좌 담은 횟수

    class Meta:
       managed = False
       db_table = 'main_lecture'


# ------------------------------------- ( 관심 강의 테이블 ) -------------------------------------

class Relation(models.Model):
    subject_num = models.ForeignKey(Lecture,on_delete=models.SET_NULL,null=True)
    student_id = models.ForeignKey(UserInfo,on_delete=models.SET_NULL,null=True)

    class Meta:
       managed = False
       db_table = 'main_relation'

# ------------------------------------- ( 강의 평가 테이블 ) -------------------------------------
class Review(models.Model):
    id = models.IntegerField(primary_key=True) # 번호
    subject_num = models.ForeignKey(Lecture,on_delete=models.SET_NULL,null=True) # 학수번호
    student_id = models.ForeignKey(UserInfo,on_delete=models.SET_NULL,null=True) # 학번
    u_year = models.IntegerField() # 수강 학년
    u_semester = models.IntegerField() # 수강 학기
    star = models.IntegerField() # 별점(1~5)
    content = models.TextField() # 평가 내용

    class Meta:
       managed = False
       db_table = 'main_review'

 # ------------------------------------- ( 검사 기준 테이블 ) -------------------------------------

class Standard(models.Model):  
    major = models.CharField(primary_key=True) # 학과 
    total = models.IntegerField() # 총졸업학점
    major_credit = models.IntegerField() # 전공학점
    s_credit = models.IntegerField() # 복수전공 학점
    major_essential = models.IntegerField() # 전공필수 학점
    major_selection = models.IntegerField # 전공선택 학점
    major_selection_list = models.CharField() # 전공선택 중 필수 이수 과목
    explore = models.IntegerField() # 대학탐구 학점
    self = models.IntegerField() # 자아성찰 학점
    civ = models.IntegerField() # 21c 시민, 미래위험사회와안전, 지역연구 학점
    writing = models.IntegerField() # 글쓰기 학점
    seminar = models.IntegerField() # 명작(세미나) 학점
    leader = models.IntegerField() # 리더십 학점
    eas = models.IntegerField() # EAS1,2 학점
    sw = models.IntegerField() # 소프트웨어 학점
    basic = models.IntegerField() # 학문 기초 학점
    basic_list_m = models.CharField() # 학문 기초 교과목 m 목록
    basic_list_s = models.CharField() # 학문 기초 교과목 s 목록
    basic_list_c = models.CharField() # 학문 기초 교과목 c 목록
    eng_major = models.IntegerField() # 전공 원어강의 학점 

    class Meta:
        managed = False
        db_table = 'main_standard'
