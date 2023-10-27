import us
from uuid import uuid4
from django.db import models
from django.utils import timezone


# ------------------------------------- ( 회원 정보 테이블 ) -------------------------------------
class NewUserInfo(models.Model):
    register_time = models.CharField(max_length=45) 
    student_id = models.CharField(primary_key=True, max_length=10) # 학번
    password = models.CharField(max_length=100) # 비밀번호
    year = models.IntegerField() # 학년
    major = models.CharField(max_length=45) # 전공
    sub_major = models.CharField(max_length=45, blank=True, null=True) # 부전공
    major_status = models.CharField(max_length=10) # 전공상태
    name = models.CharField(max_length=45) # 학생 이름
    eng = models.CharField(max_length=45) # 영어 공인 성적

#   class Meta:  # 자동 migrate 막을 때 사용
 #       managed = False
 #       db_table = 'new_user_info'

class DeleteAccountLog(models.Model): # 계정 삭제
    index = models.AutoField(primary_key=True)
    major = models.CharField(max_length=45)
    year = models.IntegerField()
    name = models.CharField(max_length=45)
    register_time = models.CharField(max_length=45)
    delete_time = models.CharField(max_length=45)

 #   class Meta:
 #       managed = False
 #       db_table = 'delete_account_log'

class UserInfo(models.Model):
    student_id = models.CharField(primary_key=True, max_length=10) # 학번
    year = models.IntegerField() # 학년
    major = models.CharField(max_length=45) # 전공
    name = models.CharField(max_length=45) # 이름
    eng = models.IntegerField() # 영어 공인 성적

 #   class Meta:
 #       managed = False
 #       db_table = 'user_info'


# ------------------------------------- ( 검사 기준 테이블 ) -------------------------------------

class Standard(models.Model):
    index = models.IntegerField(primary_key=True)
    user_year = models.IntegerField() # 수강 년도
    user_dep = models.CharField(max_length=50) # 학과
    sum_score = models.IntegerField() # 학점 총점
    major_essential = models.IntegerField() # 전필
    major_selection = models.IntegerField() #전선
    core_essential = models.IntegerField() # 교필
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
    eng_major_list = models.CharField(max_length=200, blank=True, null=True)

 #   class Meta:
 #       managed = False
 #       db_table = 'standard'

# ------------------------------------- ( 강의 정보 테이블 ) -------------------------------------

class AllLecture(models.Model):
    subject_num = models.CharField(primary_key=True, max_length=10) # 학수강좌번호
    subject_name = models.CharField(max_length=70) # 교과목명
    classification = models.CharField(max_length=45) # 이수 구분
    subject_credit = models.FloatField() # 학점

 #   class Meta:
 #      managed = False
 #       db_table = 'all_lecture'


class NewLecture(models.Model):
    subject_num = models.CharField(primary_key=True, max_length=10)

 #   class Meta:
 #     managed = False
 #       db_table = 'new_lecture'

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

 # ------------------------------------- ( 로그인 테이블 ) -------------------------------------
    
