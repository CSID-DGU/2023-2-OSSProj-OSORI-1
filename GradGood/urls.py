"""
URL configuration for GradGood project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    # 페이지 렌더링
    path('', views.r_head),
    path('statistics/', views.r_statistics),
    path('statistics_ge/',views.r_statistics_ge),
    path('a_statistics/', views.a_statistics),
    path('a_statistics_ge/',views.a_statistics_ge),
    path('login/', views.r_login),
    path('login_admin/',  views.r_login1),
    path('changePW/', views.r_changePW),
    path('mypage/', views.r_mypage),
    path('admin_/',views.r_admin_),
    path('custom/', views.r_custom),
    path('a_search/', views.a_search),
    #path('agree/', views.r_agree),
    path('custom/', views.r_custom),
    path('register/', views.r_register),
    path('admin/', views.r_register),
    path('success/', views.r_success),
    path('success_delete/', views.r_success_delete),
    path('result/', views.r_result),

     # 다른 함수사용 url 패턴
    path('f_login/', views.f_login),
    path('f_login1/', views.f_login1),
    path('f_logout/', views.f_logout),
    path('f_admin/', views.f_admin),
    path('f_mypage/', views.f_mypage),
    path('f_register/', views.f_register),
    path('f_add_custom/', views.f_add_custom),
    path('f_mod_info_ms/', views.f_mod_info_ms),
    path('f_mod_info/', views.f_mod_info),
    path('f_mod_ms_eng/', views.f_mod_ms_eng),
    path('f_mod_pw/', views.f_mod_pw),
    path('f_mod_grade/', views.f_mod_grade),
    path('f_mod_cart/', views.f_mod_cart),
    path('f_result/', views.f_result),
]

