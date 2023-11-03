from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import font_manager, rc
#path = '/Library/Fonts/AppleGothic.ttf'
#font_name = font_manager.FontProperties(fname=path).get_name()
#rc('font', family=font_name)
from selenium import webdriver
import urllib.request
import urllib.parse
import time
import re 

url = 'https://everytime.kr/timetable'
driver = webdriver.Chrome('../driver/chromedriver.exe')
driver.get(url)
time.sleep(3)
user_id = input('에브리타임 아이디를 입력해주세요.: ')
et_login = driver.find_element_by_name("userid")
et_login.clear()
et_login.send_keys(user_id)

user_pw = input('에브리타임 비밀번호를 입력해주세요.: ')
et_login = driver.find_element_by_name("password")
et_login.clear()
et_login.send_keys(user_pw)

driver.find_element_by_xpath("""//*[@id="container"]/form/p[3]/input""").click()
time.sleep(3)
while True:
    try:
        driver.find_element_by_xpath("""//*[@id="sheet"]/ul/li[3]/a""").click()
        time.sleep(2)
        break
    except:
        continue
timetable_all = pd.DataFrame()
timetable_all
graph = {}
while True:
    try:
        driver.find_element_by_xpath("""//*[@id="container"]/ul/li[1]""").click()
        time.sleep(2)
        break
    except:
        continue
for i in range(9):
    while True:
        try:
            driver.find_element_by_xpath("""//*[@id="subjects"]/div[1]/a[4]""").click()
            time.sleep(2)
            break
        except:
            continue
    while i == 0:
        try:
            driver.find_element_by_xpath("""//*[@id="subjectCategoryFilter"]/div/ul/li[2]""").click()
            time.sleep(2)
            break
        except:
            continue
    while True:
        try:
            driver.find_element_by_xpath("""//*[@id="subjectCategoryFilter"]/div/ul/ul[2]/li["""+str((i+1))+"""]""").click()
            time.sleep(2)
            break
        except:
            continue
#     while True:
#         try:
#             driver.find_element_by_xpath("""//*[@id="subjectCategoryFilter"]/div/ul/ul[2]/ul["""+str((i+1))+"""]/li""").click()
#             time.sleep(2)
#             break
#         except:
#             continue
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    contents = []
    tmp = soup.find('div','list').find('tbody').find_all('td')
    for i in tmp:
        tmp = i.get_text()
        contents.append(tmp)
    contents = np.array(contents)
    column = []
    tmp = tmp = soup.find('div','list').find('thead').find_all('th')
    for i in tmp:
        tmp = str(i).lstrip('<th>').split('<div>')
        column.append(tmp[0])
    timetable = pd.DataFrame(contents.reshape(len(contents)//12,12), columns=column)
    del(timetable['계획서']) ;del(timetable['강의평'])
    major = soup.find('a','item active').get_text().split(':')[1]
    graph[str(major)] = len(timetable)
    timetable_all = pd.concat([timetable_all,timetable],ignore_index=True)
    timetable.to_excel('../data/23년 2학기 '+major+' 강좌.xls',encoding = 'cp949',sheet_name=major,index = False) # 학과 별로 저장
timetable_all.to_excel('../data/23년 2학기 공과대학 강좌.xls',encoding = 'cp949',sheet_name=major,index = False) # 공대 전체 데이터 저장
time.sleep(2)
driver.close()

timetable = pd.read_excel('../data/에브리타임 강좌.xls', encoding = 'cp949')