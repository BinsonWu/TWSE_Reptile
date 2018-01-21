#coding=UTF-8

#為了解決中文比較問題
from __future__ import unicode_literals

from selenium import webdriver

import urllib2
from bs4 import BeautifulSoup

import pandas as pd

import MySQLdb

import numpy as np

import os
import time
import csv

#Chrome Drive
Chrome_Driver_Path = "/usr/lib/chromium-browser/chromedriver"
url_StockData      = "http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAYMAIN.php"
url_ID             = "http://pchome.megatime.com.tw/search"

driver = webdriver.Chrome(Chrome_Driver_Path)
driver.get(url_StockData)

search_input = driver.find_element_by_name('stockNo')       # 取得搜尋框
search_input.clear()                                        # 清空資料
search_input.send_keys('0050')                              # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

select_month = driver.find_element_by_name('mm')
month_all_options = select_month.find_elements_by_tag_name("option")
for option in month_all_options:
    option_month = option.text[:2]
    if(int(option_month) == 7):
        month_info = str(int(option_month))+"月"
        print(month_info)
        option.click()
        #搜尋
        driver.find_element_by_link_text("查詢").click()
        time.sleep(1)

        #觀察 result-message
        page = driver.page_source
        soup = BeautifulSoup(page)
        result_message = soup.find("div", {"id": "result-message"})
        print("result-message:")
        print(result_message.text)
        time.sleep(1)

        #Test
        if(result_message.text == u'查詢日期大於今日，請重新查詢!'):
            print("大於!!!")

        #如果沒有 result_message 才做
        if not result_message.text:
            print("None!")

            # 下載CSV
            print(driver.find_element_by_class_name("csv").text)
            driver.find_element_by_class_name("csv").click()

            #等到下載完
            print("Wait For Download...")
            isExists = None
            while not isExists:
                isExists = os.path.exists('/home/dclab/下載/STOCK_DAY.csv')
            print("Download Finish!")
            time.sleep(1)


            #載完後開檔
            f = open('/home/dclab/下載/STOCK_DAY.csv', 'r')
            counter = 0;
            for row in csv.reader(f):
                if (len(row) == 10 and counter > 1):
                    print row[0]
                counter = counter + 1
            f.close()

            #讀完後關檔
            os.remove("/home/dclab/下載/STOCK_DAY.csv")

            #等到刪除CSV檔後再跑下一個
            print("Wait For Delete...")
            while isExists:
                isExists = os.path.exists('/home/dclab/下載/STOCK_DAY.csv')
            print("Delete Finish!")

# 關閉網站
driver.quit()


#df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

