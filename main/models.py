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

class UserInfo(models.Model): # 회원가입
    student_id = models.CharField(primary_key=True, max_length=10) # 학번 입력요구
    password = models.CharField(max_length=100, validators=[password_validator]) # 비밀번호
    year = models.IntegerField() # 학년
    major = models.CharField(max_length=45) # 전공
    sub_major = models.CharField(max_length=45, blank=True, null=True) # 부전공
    name = models.CharField(max_length=45) # 학생 이름
    thesis = models.IntegerField() # 졸업논문(시험) 통과여부(o,x)
    eng = models.IntegerField() # 영어 공인 성적(토익기준)

 #   class Meta:  # 자동 migrate 막을 때 사용
 #       managed = False
 #       db_table = 'user_info'


class UserGrade(models.Model): # 수강한 과목 정보 및 성적 (직접 졸업요건 입력)
    student_id = models.CharField(max_length=10) # 학번
    major = models.CharField(max_length=45, blank=True, null=True) # 전공
    user_year = models.IntegerField() # 수강 년도
    semester = models.CharField(max_length=45) # 수강 학기
    classification = models.CharField(max_length=45) # 이수 구분
    subject_num = models.CharField(max_length=10) # 학수강좌번호
    subject_name = models.CharField(max_length=70) # 교과목명
    subject_credit = models.IntegerField() # 학점
    grade = models.FloatField() # 등급
    eng_class = models.CharField(max_length=50) # 원어 강의 종류
    index = models.AutoField(primary_key=True) # 인덱스

 #   class Meta:
 #       managed = False
 #       db_table = 'user_grade'


class MyInfo(models.Model): # 내정보
    student_id = models.CharField(primary_key=True, max_length=10) # 학번
    major = models.CharField(max_length=45) # 학과
    name = models.CharField(max_length=45) # 이름
    thesis = models.IntegerField() # 졸업논문/시험 통과 여부
    eng = models.IntegerField() # 영어 공인 성적

 #   class Meta:
 #       managed = False
 #       db_table = 'my_info'

# ------------------------------------- ( 검사 기준 테이블 ) -------------------------------------

class Standard(models.Model):
    index = models.IntegerField(primary_key=True)
    user_year = models.IntegerField() # 수강 년도
    user_dep = models.CharField(max_length=50) # 학과
    sum_score = models.IntegerField() # 학점 총점
    major_essential = models.IntegerField() # 전필
    major_selection = models.IntegerField() #전선
    core_essential = models.IntegerField() # 교필
 #   core_selection = models.IntegerField() # ?
    la_balance = models.IntegerField() # 학점
    basic = models.IntegerField() 
    ce_list = models.CharField(max_length=100)
    cs_list = models.CharField(max_length=100)
    b_list = models.CharField(max_length=100)
    english = models.JSONField()
    sum_eng = models.IntegerField()
    pro = models.IntegerField(blank=True, null=True)
    bsm = models.IntegerField(blank=True, null=True)
    eng_major = models.IntegerField(blank=True, null=True)
    build_sel_num = models.IntegerField(blank=True, null=True)
#    pro_ess_list = models.CharField(max_length=100, blank=True, null=True)
#    bsm_ess_list = models.CharField(max_length=100, blank=True, null=True)
#    bsm_sel_list = models.CharField(max_length=100, blank=True, null=True)
#    build_start = models.CharField(max_length=10, blank=True, null=True)
#    build_sel_list = models.CharField(max_length=100, blank=True, null=True)
#    build_end = models.CharField(max_length=10, blank=True, null=True)
    eng_major_list = models.CharField(max_length=200, blank=True, null=True)

 #   class Meta:
 #       managed = False
 #       db_table = 'standard'

# ------------------------------------- ( 강의 정보 테이블 ) -------------------------------------

class AllMajor(models.Model): # 꿀전공 목록
    subject_num = models.CharField(primary_key=True, max_length=10) # 학수번호
    subject_name = models.CharField(max_length=70) # 과목명
    classification = models.CharField(max_length=45) # 이수구분 
    professor = models.CharField(max_length=50) # 담당교원
    subject_credit = models.FloatField() # 학점

 #   class Meta:
 #      managed = False
 #       db_table = 'all_major'

class AllGE(models.Model): # 꿀교양 목록
    subject_num = models.CharField(primary_key=True, max_length=10) # 학수번호
    subject_name = models.CharField(max_length=70) # 과목명
    classification_GE = models.CharField(max_length=45) # 이수구분영역 
    professor = models.CharField(max_length=50) # 담당교원
    subject_credit = models.FloatField() # 학점

 #   class Meta:
 #      managed = False
 #       db_table = 'all_ge'


class NewLecture(models.Model):
    subject_num = models.CharField(primary_key=True, max_length=10)

 #   class Meta:
 #     managed = False
 #       db_table = 'new_lecture'

# ------------------------------------- ( 관심 강의 테이블 ) -------------------------------------

class MajorIn(models.Model): # 관심 전공 목록
    subject_num = models.CharField(primary_key=True, max_length=10) # 학수번호
    subject_name = models.CharField(max_length=70) # 과목명
    classification = models.CharField(max_length=45) # 이수구분 
    professor = models.CharField(max_length=50) # 담당교원
    subject_credit = models.FloatField() # 학점

 #   class Meta:
 #      managed = False
 #       db_table = 'major_in'

class GEIn(models.Model): # 관심 교양 목록
    subject_num = models.CharField(primary_key=True, max_length=10) # 학수번호
    subject_name = models.CharField(max_length=70) # 과목명
    classification_GE = models.CharField(max_length=45) # 이수구분영역 
    professor = models.CharField(max_length=50) # 담당교원
    subject_credit = models.FloatField() # 학점

 #   class Meta:
 #      managed = False
 #       db_table = 'ge_in'

# ------------------------------------- ( 강의 평가 테이블 ) -------------------------------------
class Review(models.Model):
    index = models.IntegerField(primary_key=True) # 강의 평가 번호
    u_year = models.IntegerField() # 수강 학년
    u_semester = models.IntegerField() # 수강 학기
    star = models.IntegerField() # 별점(1~5)
    content = models.TextField() # 평가 내용

 #   class Meta:
 #      managed = False
 #       db_table = 'review'

# ------------------------------------- ( 브라우저 세션/쿠키 ) -------------------------------------

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

 #    class Meta:
 #       managed = False
 #       db_table = 'django_session'


class VisitorCount(models.Model):
    visit_date = models.CharField(primary_key=True, max_length=45)
    visit_count = models.IntegerField()
    user_count = models.IntegerField(blank=True, null=True)
    signup_count = models.IntegerField(blank=True, null=True)
    delete_count = models.IntegerField(blank=True, null=True)

 #   class Meta:
 #       managed = False
 #       db_table = 'visitor_count'


# ------------------------------------- ( 매핑 테이블 ) -------------------------------------

class Major(models.Model):
    index = models.AutoField(primary_key=True)
    college = models.CharField(max_length=45)
    department = models.CharField(max_length=45, blank=True, null=True)
    major = models.CharField(max_length=45)
    sub_major = models.CharField(max_length=45, blank=True, null=True)

 #   class Meta:
 #       managed = False
 #       db_table = 'major'


class SubjectGroup(models.Model):
    subject_num = models.CharField(primary_key=True, max_length=10)
    group_num = models.CharField(max_length=10)

 #   class Meta:
 #       managed = False
 #       db_table = 'subject_group'


class ChangedClassification(models.Model):
    index = models.IntegerField(primary_key=True)
    subject_num = models.CharField(max_length=10)
    year = models.IntegerField()
    classification = models.CharField(max_length=10)

 #   class Meta:
 #       managed = False
 #       db_table = 'changed_classification'
    
