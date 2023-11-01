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

class UserInfo(models.Model): # 
    student_id = models.CharField(primary_key=True, max_length=10) # 학번 입력요구
    password = models.CharField(max_length=100, validators=[password_validator]) # 비밀번호
    year = models.IntegerField() # 학년
    major = models.CharField(max_length=45) # 전공
    sub_major = models.CharField(max_length=45, blank=True, null=True) # 부전공
    name = models.CharField(max_length=45) # 학생 이름
    thesis = models.BooleanField() # 졸업논문(시험) 통과여부(o,x)
    eng = models.IntegerField(blank=True, null=True) # 영어 공인 성적(토익기준)
    eg = models.BooleanField() # 공대/비공대 여부
    sum_credit = models.IntegerField() # 총 졸업학점

 #   class Meta:  # 자동 migrate 막을 때 사용
 #       managed = False
 #       db_table = 'user_info'

# ------------------------------------- ( 강의 정보 테이블 ) -------------------------------------

class Lecture(models.Model):
    subject_num = models.CharField(primary_key=True, max_length=10)
    subject_name = models.CharField(max_length=70)
    classification = models.CharField(max_length=45)
    classification_ge = models.CharField(max_length=45)
    professor = models.CharField(max_length=50)
    subject_credit = models.IntegerField()
    major_ge = models.BooleanField()

 #   class Meta:
 #      managed = False
 #       db_table = 'lecture'

# ------------------------------------- ( 관심 강의 테이블 ) -------------------------------------

class relation(models.Model):
    subject_num = models.CharField(max_length=10)
    student_id = models.CharField(max_length=10)

 #   class Meta:
 #      managed = False
 #       db_table = 'relation'

# ------------------------------------- ( 강의 평가 테이블 ) -------------------------------------
class Review(models.Model):
    id = models.IntegerField(primary_key=True) # 번호
    subject_num = models.CharField(max_length=10)
    student_id = models.CharField(max_length=10)
    u_year = models.IntegerField() # 수강 학년
    u_semester = models.IntegerField() # 수강 학기
    star = models.IntegerField() # 별점(1~5)
    content = models.TextField() # 평가 내용

 #   class Meta:
 #      managed = False
 #       db_table = 'review'

 # ------------------------------------- ( 검사 기준 테이블 ) -------------------------------------

class Standard(models.Model):
    index = models.IntegerField(primary_key=True)
    classification = models.CharField(max_length=45)
    classification_ge = models.CharField(max_length=45)
    subject_num = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=70)
    subject_credit = models.IntegerField()
    delete = models.BooleanField()
    msc = models.CharField(70)
    msc_type = models.CharField(70)
    eng_sub = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'standard'