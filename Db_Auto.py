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


class DataBase_Service:
  def __init__(self):
    # Control Var
    self.host           = "localhost"
    self.user           = "root"
    self.password       = ""
    self.database       = ""
    self.ID_Table_Name  = ""
    self.CashDividend_Table_Name = ""

    #Chrome Drive
    self.Chrome_Driver_Path = "/usr/lib/chromium-browser/chromedriver"
    self.url_StockData      = "http://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html"
    self.url_ID             = "http://pchome.megatime.com.tw/search"

    #Connect Var
    self.db             = MySQLdb.connect(self.host, self.user, self.password, self.database, charset='utf8')
    self.cursor         = self.db.cursor()

    # All ID & Name of The Type of Stock U Want
    self.ID_table       = []
    self.Name_table     = []
    self.newID_table    = []
    self.newName_table  = []

    #CashDividend
    self.CashDividendIDtable = []

    #Set ID_table Name_table
    sql = "SELECT * FROM " + self.ID_Table_Name
    # 執行SQL statement
    self.cursor.execute(sql)
    # 撈取多筆資料
    results = self.cursor.fetchall()
    # 迴圈撈取資料
    for record in results:
      self.ID_table.append( record[0] )
      self.Name_table.append(record[1])

    # Set ID_table Name_table
    sql = "SELECT * FROM " + self.CashDividend_Table_Name
    # 執行SQL statement
    self.cursor.execute(sql)
    # 撈取多筆資料
    results = self.cursor.fetchall()
    # 迴圈撈取資料
    for record in results:
      self.CashDividendIDtable.append(record[0])

  # <---------- DataBase OperateI ---------->
  #Order
  def INSERT(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令
    self.db.commit()

  def DROP(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令

  def SELECT(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令
    return self.cursor.fetchall()

  def UPDATE(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令
    self.db.commit()

  def ALTER(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令

  def CREATE(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令

  def TRUNCATE(self,sql):
    print sql
    self.cursor.execute(sql)  # 執行指令

  # Add a new Column_Name to Table
  def Add_Table_Column(self,Table_Name,Column_Name,Column_Type):
    sql = "ALTER TABLE " + Table_Name + " ADD " + Column_Name + " " + Column_Type
    self.ALTER(sql)

  def Add_allStockTable_Column(self,Column_Name,Column_Type):
    for nID in range(len(self.ID_table)):
      try:
        print("Stock %d" % nID)
        Table_Name = self.ID_table[nID] + "_" + self.Name_table[nID]
        sql = "ALTER TABLE " + Table_Name + " ADD " + Column_Name + " " + Column_Type
        '''sql = "ALTER TABLE " + Table_Name + " ADD MA3 float not null,ADD MA5 float not null," \
                                            "ADD MA10 float not null,ADD MA20 float not null," \
                                            "ADD MA60 float not null,ADD MA240 float not null"'''
        self.ALTER(sql)
      except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])

  def Drop_allStockTable_Column(self, Column_Name):
    for nID in range(len(self.ID_table)):
      try:
        print("Stock %d" % nID)
        Table_Name = self.ID_table[nID] + "_" + self.Name_table[nID]
        sql = "ALTER TABLE " + Table_Name + " DROP COLUMN " + Column_Name
        self.DROP(sql)
      except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])

  # <---------- Provite Var API ---------->
  def getDataBase_Service_Var(self,type):
    if type == "host":
      return self.host
    if type == "user":
      return self.user
    if type == "password":
      return self.password
    if type == "database":
      return self.database
    if type == "ID_Table_Name":
      return self.ID_Table_Name
    if type == "ID_table":
      return self.ID_table
    if type == "Name_table":
      return self.Name_table
    print("Fail! No Type...")

  def setDataBase_Service_Var(self,type,newvalue):
    if type == "host":
      self.host           = newvalue
      print("Set Success")
    elif type == "user":
      self.user           = newvalue
      print("Set Success")
    elif type == "password":
      self.password       = newvalue
      print("Set Success")
    elif type == "database":
      self.database       = newvalue
      print("Set Success")
    elif type == "ID_Table_Name":
      self.ID_Table_Name  = newvalue
      print("Set Success")
    else:
      print("Set Fail!!!")

  #<---------- Data from Website ---------->
  # 得到ID -> EX 得到 台灣 '上市股' 的 全部股票的ID (上市股 ListedShares)
  def getTW_oneTypeStock_All_ID(self,select_Stock_Type):
    # Drive Chrome
    driver = webdriver.Chrome(self.Chrome_Driver_Path)
    driver.get(self.url_ID)

    stock_type = driver.find_element_by_name('select1')
    stock_type_options = stock_type.find_elements_by_tag_name("option")
    for option in stock_type_options:
      if option.text == select_Stock_Type.decode('utf-8'):
        option.click()

    # Press 確定
    button = driver.find_element_by_xpath("//input[@value='　確 定　']")
    button.click()

    # 抓到所有筆資料 (有好幾頁)
    # 計算有幾頁
    div_pages = driver.find_element_by_xpath("//div[@class='pages']")
    print("共有 %s 筆" % div_pages.text[22:25])
    n_page = int(div_pages.text[22:25]) / 200 + 1
    print("共有 %d 頁" % n_page)

    # 開始抓取ID
    print("---> Start to Get ID")
    for i in range(1, n_page + 1, 1):
      print("In Page %d :" % i)
      a = None
      if i != 1:
        print("page %s" % str(i))
        a = driver.find_element_by_link_text(str(i))

      if a != None or i == 1:
        if a != None:
          a.click()
        page = driver.page_source

        soup = BeautifulSoup(page)

        div = soup.find('div', id='stocks_list_table')
        table = div.find(lambda tag: tag.name == 'table')
        tbody = table.find('tbody')
        for row in tbody.find_all("tr"):
          data = row.find_all("td")
          if data:
            # prevent list index out of range
            for data_num in range(len(data)):
              # print data[data_num].find(text=True),
              getID = ""
              getName = ""
              for j in range(len(data[data_num].find(text=True))):
                if data[data_num].find(text=True)[j] == ' ':
                  break
                getID = getID + data[data_num].find(text=True)[j]
              j = j + 1
              for k in range(j, len(data[data_num].find(text=True)), 1):
                if data[data_num].find(text=True)[k] == '-':
                  break
                getName = getName + data[data_num].find(text=True)[k]

              self.newID_table.append(getID)
              self.newName_table.append(getName)
              print("%12s %15s" % (getID, getName)),
          print ("")
      else:
        break
    print("---> End to Get ID")
    driver.quit()

  def Add_All_ID_to_Mysql(self):
    # 加入所有抓到的資料到Mysql 指定 Table
    for i in range(len(self.newID_table)):
      sql = "INSERT INTO Stock_ID_Name(ID,Name,Record_High,Record_Low) values('" \
            + self.newID_table[i] + "','" + self.newName_table[i] + "','0','0')"
      self.INSERT(sql)

  # ID & Name Add to MySQL
  def Add_ID_to_Mysql(self):
    # 加入所有抓到的資料到Mysql 指定 Table
    for i in range(len(self.newID_table)):
      sql = "INSERT INTO Stock_ID_Name(ID,Name,Record_High,Record_Low) values('" \
            + self.newID_table[i] + "','" + self.newName_table[i] + "','0','0')"
      self.INSERT(sql)

  #將所有沒DayAve的設為 (OPP+CLP)/2
  def Set_All_MA(self):
    print("----> Start to Set MA")
    for nID in range(0,len(self.ID_table),1):
      try:
        print("Stock %d" % nID)
        sql = "select Date,ClosingPrice from " + self.ID_table[nID] + "_" + self.Name_table[nID]
        results = self.SELECT(sql)
        #EX: update 0050_元大台灣50 set DayAve = 73.4 where Date = '106/02/18'
        date_arr = []
        clsp_arr   = []
        for record in results:
          date_arr.append(record[0])
          clsp_arr.append(record[1])
        for i in range(len(date_arr)):
          MA3   = clsp_arr[i]
          MA5   = clsp_arr[i]
          MA10  = clsp_arr[i]
          MA20  = clsp_arr[i]
          MA60  = clsp_arr[i]
          MA240 = clsp_arr[i]
          if i >= 2:
            MA3   = ( np.average(clsp_arr[i-2   :i+1]) )
          if i >= 4:
            MA5   = ( np.average(clsp_arr[i-4   :i+1]) )
          if i >= 9:
            MA10  = ( np.average(clsp_arr[i-9   :i+1]) )
          if i >= 19:
            MA20  = ( np.average(clsp_arr[i-19  :i+1]) )
          if i >= 59:
            MA60  = ( np.average(clsp_arr[i-59  :i+1]) )
          if i >= 239:
            MA240 = ( np.average(clsp_arr[i-239 :i+1]) )
          new_MA3   = "%.2f" % MA3
          new_MA5   = "%.2f" % MA5
          new_MA10  = "%.2f" % MA10
          new_MA20  = "%.2f" % MA20
          new_MA60  = "%.2f" % MA60
          new_MA240 = "%.2f" % MA240
          #print("MA 3 5 10 20 60 240 : %f %f %f %f %f %f" % (MA3,MA5,MA10,MA20,MA60,MA240) )
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA3 = "   + str(new_MA3)      + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA5 = "   + str(new_MA5)      + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA10 = "  + str(new_MA10)     + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA20 = "  + str(new_MA20)     + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA60 = "  + str(new_MA60)     + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
          sql = "UPDATE " + self.ID_table[nID]  + "_" + self.Name_table[nID] + \
                " SET MA240 = " + str(new_MA240)    + " WHERE Date = '" + date_arr[i] + "'"
          self.UPDATE(sql)
      except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])
      print("----> End to Set MA\n\n")

  # 得到單支股票歷年資料
  def getOne_Stock_All_Data_to_Mysql(self,Which_Stock, Which_Table):
    # Create DataFrame
    df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

    # Drive Chrome
    driver = webdriver.Chrome(self.Chrome_Driver_Path)
    driver.get(self.url_StockData)
    search_input = driver.find_element_by_name('stockNo')         # 取得搜尋框
    search_input.send_keys(Which_Stock)                         # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

    # 每刷新一次頁面element都要重新取得

    # 得到 幾年到幾年
    select_year = driver.find_element_by_name('yy')
    year_all_options = select_year.find_elements_by_tag_name("option")

    newest_year = int(select_year.find_elements_by_tag_name("option")[0].text)
    earliest_year = 0
    for option in year_all_options:
      earliest_year = int(option.text)
    print earliest_year
    print newest_year
    print("---> Start to Get Data")
    # 利用 loop 把每個選項都跑過
    for i in range(90, newest_year + 1, 1):
      print("Year : %d" % i)
      select_year = driver.find_element_by_name('yy')
      year_all_options = select_year.find_elements_by_tag_name("option")
      for option in year_all_options:
        if i == int(option.text):
          option.click()

      for j in range(1, 13, 1):
        print j
        select_month = driver.find_element_by_name('mm')
        month_all_options = select_month.find_elements_by_tag_name("option")

        for option in month_all_options:
          if j == int(option.text):
            option.click()

        # 令 chrome driver 按下 submit 觸發按鈕
        driver.find_element_by_link_text("查詢").click()

        # Delay
        time.sleep(1)

        # 查詢這個月的 "結果訊息" 為何
        page = driver.page_source
        soup = BeautifulSoup(page)
        result_message = soup.find("div", {"id": "result-message"})
        print("Result Message :")
        if result_message.text:
          print(result_message.text)
        else:
          print("None!")

        # 判斷有無資料
        if result_message.text != u'查詢日期大於今日，請重新查詢!' and result_message.text != u'很抱歉，沒有符合條件的資料!':
          div = soup.find('div', id='main-content')
          table = div.find(lambda tag: tag.name == 'table')
          tbody = table.find('tbody')
          for row in tbody.find_all("tr"):
            data = row.find_all("td")
            One_Profile = []
            Date = data[0].find(text=True)
            oriOp = data[3].find(text=True)
            oriCl = data[6].find(text=True)
            oriFp = data[5].find(text=True)
            oriHp = data[4].find(text=True)
            if (oriOp == u'--'):
              continue
            newOp = ""
            newCl = ""
            newFp = ""
            newHp = ""
            for nch in range(len(oriOp)):
              if oriOp[nch] != u',':
                newOp = newOp + oriOp[nch]
            for nch in range(len(oriCl)):
              if oriCl[nch] != u',':
                newCl = newCl + oriCl[nch]
            for nch in range(len(oriFp)):
              if oriFp[nch] != u',':
                newFp = newFp + oriFp[nch]
            for nch in range(len(oriHp)):
              if oriHp[nch] != u',':
                newHp = newHp + oriHp[nch]
            One_Profile.append(Date)
            One_Profile.append(newOp)
            One_Profile.append(newCl)
            One_Profile.append(newFp)
            One_Profile.append(newHp)
            df.loc[len(df)] = One_Profile

    driver.quit()

    print("---> End to Get Data")

    print ("")
    print("DataFrame:")
    print df
    print ("")

    # 取得 MySQL DataBase 資料
    try:
      # 建立DB 連線資訊定設定中文編碼utf-8
      print("---> Start Add Data")
      # 加入所有抓到的資料到Mysql 指定 Table
      # 先前成功的指令
      # INSERT INTO DataFrame(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('106/02/02','73.50','72.90','72.75','73.65');
      for i in range(len(df)):
        sql = "INSERT INTO " + Which_Table.decode('utf8') + "(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('" \
              + df.iat[i, 0] + "','" + df.iat[i, 1] + "','" + df.iat[i, 2] + "','" + df.iat[i, 3] + "','" + df.iat[i, 4] + "')"
        self.INSERT(sql)
      print("---> End to Add Data\n\n")

    except MySQLdb.Error as e:
      print "Error %d: %s" % (e.args[0], e.args[1])

  # 得到所有股票歷年資料
  def getAll_Stock_All_Data_to_Mysql(self):
    # 連上網站
    driver = webdriver.Chrome(self.Chrome_Driver_Path)
    driver.get(self.url_StockData)

    # 依 ID_Table 第0支股票開始
    for nID in range(len(self.ID_table)):
      try:
        print("\n<--------------------------->")
        print("Get Stock %d : %s_%s " % (nID, self.ID_table[nID], self.Name_table[nID]))
        # Set Which Stock
        Which_Stock = self.ID_table[nID]

        # Create DataFrame
        df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

        print("search_input");
        # Drive Chrome Input Which Stock ID We Want
        search_input = driver.find_element_by_name('stockNo')  # 取得搜尋框
        print(search_input.tag_name);
        search_input.clear()  # 清空資料
        search_input.send_keys(Which_Stock)  # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

        print("search_form");
        #search_form = driver.find_element_by_classname("main ajax")
        #print(search_form.text);
        print("search_div");
        search_div = driver.find_element_by_id('dl')
        print(search_div.text);
        # 得到 幾年到幾年
        select_year = driver.find_element_by_name('yy')
        print(select_year.text);
        year_all_options = select_year.find_elements_by_tag_name("option")

        newest_year = int(select_year.find_elements_by_tag_name("option")[0].text)
        earliest_year = 0
        for option in year_all_options:
          print(option.text);
          earliest_year = int(option.text)

        # print("Search From %s to %s" % (earliest_year,newest_year))

        print("---> Start to Get Data")
        # 利用 loop 把每個選項都跑過 即 '每年' '每月'
        for i in range(earliest_year, newest_year + 1, 1):
          # print("Year : %d" % i)
          select_year = driver.find_element_by_name('yy')
          year_all_options = select_year.find_elements_by_tag_name("option")
          for option in year_all_options:
            if i == int(option.text):
              option.click()

          for j in range(1, 13, 1):
            # print j
            select_month = driver.find_element_by_name('mm')
            month_all_options = select_month.find_elements_by_tag_name("option")

            for option in month_all_options:
              if j == int(option.text):
                option.click()

            # 令 chrome driver 按下 submit 觸發按鈕
            driver.find_element_by_link_text("查詢").click()

            # Delay
            time.sleep(1)

            # 查詢這個月的 "結果訊息" 為何
            page = driver.page_source
            soup = BeautifulSoup(page)
            result_message = soup.find("div", {"id": "result-message"})
            print("Result Message :")
            if result_message.text:
              print(result_message.text)
            else:
              print("None!")

            # 判斷有無資料
            if result_message.text != u'查詢日期大於今日，請重新查詢!' and result_message.text != u'很抱歉，沒有符合條件的資料!':
              div = soup.find('div', id='main-content')
              table = div.find(lambda tag: tag.name == 'table')
              tbody = table.find('tbody')
              for row in tbody.find_all("tr"):
                data = row.find_all("td")
                One_Profile = []
                Date = data[0].find(text=True)
                oriOp = data[3].find(text=True)
                oriCl = data[6].find(text=True)
                oriFp = data[5].find(text=True)
                oriHp = data[4].find(text=True)
                if (oriOp == u'--'):
                  continue
                newOp = ""
                newCl = ""
                newFp = ""
                newHp = ""
                for nch in range(len(oriOp)):
                  if oriOp[nch] != u',':
                    newOp = newOp + oriOp[nch]
                for nch in range(len(oriCl)):
                  if oriCl[nch] != u',':
                    newCl = newCl + oriCl[nch]
                for nch in range(len(oriFp)):
                  if oriFp[nch] != u',':
                    newFp = newFp + oriFp[nch]
                for nch in range(len(oriHp)):
                  if oriHp[nch] != u',':
                    newHp = newHp + oriHp[nch]
                One_Profile.append(Date)
                One_Profile.append(newOp)
                One_Profile.append(newCl)
                One_Profile.append(newFp)
                One_Profile.append(newHp)
                df.loc[len(df)] = One_Profile
        print("---> End to Get Data")

        # ---------------------------------------------------------------------------------------------------------------

        # 取得 MySQL DataBase 資料
        try:
          print("---> Start Add Data")
          # Create This Stock Table
          Name_of_Table = self.ID_table[nID] + "_" + self.Name_table[nID]
          sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null,FloorPrice float not null,HighestPrice float not null)character set = utf8"
          self.CREATE(sql)

          # 加入所有抓到的資料到Mysql 指定 Table ( 沒有table就創一個 )
          # 先前成功的指令
          # INSERT INTO DataFrame(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('106/02/02','73.50','72.90','72.75','73.65');
          for i in range(len(df)):
            # Insert
            sql = "INSERT INTO " + Name_of_Table + "(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('" \
                  + df.iat[i, 0] + "','" + df.iat[i, 1] + "','" + df.iat[i, 2] + "','" + df.iat[i, 3] + "','" + df.iat[
                    i, 4] + "')"
            self.INSERT(sql)
          print("---> End to Add Data\n\n")

        except MySQLdb.Error as e:
          print "Error %d: %s" % (e.args[0], e.args[1])
      except e:
        print("**********************")
        print("   Reload Stock %d" % nID)
        print("**********************")
        # 關閉網站
        driver.quit()
        # 連上網站
        driver = webdriver.Chrome(self.Chrome_Driver_Path)
        driver.get(self.url_StockData)
        nID = nID - 1

    # 關閉網站
    driver.quit()

  # 得到所有上市股配股配息
  def getAllCashDividedData(self):
    print("getAllCashDividedData")
    #url = "http://stock.wespai.com/p/3933"
    url = "http://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID=0056"

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    if soup != None:
      print("Success!!!")

    print(soup.prettify())

    '''tbody = soup.find("tbody")
    for row in tbody.find_all("tr"):
      data = row.find_all("td")
      print data'''

    '''Name_of_Table = self.ID_table[nID] + "_" + self.Name_table[nID]
    sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null,FloorPrice float not null,HighestPrice float not null)character set = utf8"
    self.CREATE(sql)'''

  # Auto Insert Newest & Delete Unexist Stock
  def Update_ID_Table(self,select_Stock_Type):
    print("Updating ID_Table...")
    self.getTW_oneTypeStock_All_ID(select_Stock_Type)

    add_num = 0                       #判斷有沒有  增加
    rem_num = 0                       #判斷有沒有  減少
    ori_n   = 0                       #操作本來的  IDTABLE
    new_n   = 0                       #操作新的    IDTABLE
    ori_l   = len(self.ID_table)
    new_l   = len(self.newID_table)
    while(1):
      ori_ID    = self.ID_table[ori_n]
      new_ID    = self.newID_table[new_n]
      ori_Name  = self.Name_table[ori_n]
      new_Name  = self.newName_table[new_n]

      if ori_ID > new_ID:   #代表多一支股票 新增table
        print(">  Ori:%8s, New:%8s" % (ori_ID, new_ID))
        add_num = add_num + 1
        Name_of_Table = new_ID + "_" + new_Name
        sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null," \
                                                "FloorPrice float not null,HighestPrice float not null," \
                                                "MA3 float not null,MA5 float not null,MA10 float not null," \
                                                "MA20 float not null,MA60 float not null,MA240 float not null)character set = utf8"
        self.CREATE(sql)
        if new_n + 1 < new_l:
          new_n = new_n + 1
      elif ori_ID < new_ID:   #代表少一支股票 刪除table
        print("<  Ori:%8s, New:%8s" % (ori_ID, new_ID))
        rem_num = rem_num + 1
        Name_of_Table = ori_ID + "_" + ori_Name
        sql = "drop table " + Name_of_Table
        self.DROP(sql)
        if ori_n + 1 < ori_l:
          ori_n = ori_n + 1
      elif ori_ID == new_ID:  #代表兩股票相同
        if new_n + 1 < new_l:
          new_n = new_n + 1
        if ori_n + 1 < ori_l:
          ori_n = ori_n + 1

      if new_n + 1 == new_l and ori_n + 1 == ori_l:           #代表都到最後一筆了
        #print("Final!!! Ori:%8s, New:%8s" % (self.ID_table[ori_n], self.newID_table[new_n]))
        if self.ID_table[ori_n] != self.newID_table[new_n]:   #不一樣代表要 '刪除' '舊的最後一筆'
                                                              #           '新增' '新的最後一筆'
          Name_of_Table = self.newID_table[new_n] + "_" + self.newName_table[new_n]
          sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null,FloorPrice float not null,HighestPrice float not null)character set = utf8"
          self.CREATE(sql)
          Name_of_Table = self.ID_table[new_n] + "_" + self.Name_table[new_n]
          sql = "drop table " + Name_of_Table
          self.DROP(sql)
        break

    if add_num != 0 or rem_num != 0:
      # 最後直接把舊的表清空加入新的
      sql = "truncate table Stock_ID_Name"
      self.TRUNCATE(sql)

      self.Add_All_ID_to_Mysql()

      self.ID_table = self.newID_table
      self.Name_table = self.newName_table
      self.newID_table = []
      self.newName_table = []
      print("OK!!!")
    else:
      print("Already the Newest!!!")
    print("Updating END!!!\n\n")

  # Auto Insert Newest Data Day by Day
  def Update_Stock_Data(self):
    print("Updating Stock_Data...")
    # 連上網站
    driver = webdriver.Chrome(self.Chrome_Driver_Path)
    driver.get(self.url_StockData)

    # 依 ID_Table 第0支股票開始
    for nID in range(26,len(self.ID_table),1):
      try:
        print("\n\n<--------------------------->")
        print("Get Stock %d : %s_%s " % (nID, self.ID_table[nID], self.Name_table[nID]))
        # Set Which Stock
        Which_Stock = self.ID_table[nID]
        # Create DataFrame
        df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])
        # Drive Chrome Input Which Stock ID We Want
        search_input = driver.find_element_by_name('stockNo')     # 取得搜尋框
        search_input.clear()                                      # 清空資料
        search_input.send_keys(Which_Stock)                       # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

        print("---> Start to Get Data")
        select_month  = driver.find_element_by_name('mm')
        select_year   = driver.find_element_by_name('yy')
        
        # 抓到現在的值
        now_month = int( select_month.get_attribute("value") )
        now_year  = int(select_year.get_attribute("value"))
        month_arr = []
        if now_month == 1:
          month_arr.append(12)
        else:
          month_arr.append( now_month - 1 )
        month_arr.append(now_month)
        
        # 抓到最新兩個月
        for i in range(2):
          select_month = driver.find_element_by_name('mm')
          month_all_options = select_month.find_elements_by_tag_name("option")
          for option in month_all_options:
            option_month = option.text[:2]
            if month_arr[i] == int(option_month):
              option.click()

          #代表要搜尋 前年12 , 今年1 月，年要換。
          #counter = 1 代表前一年，counter = 0 代表今年
          counter = 0;
          #搜尋前一年12月
          if(month_arr[i] == 12 and i == 0):
            select_year = driver.find_element_by_name('yy')
            year_all_options = select_year.find_elements_by_tag_name("option")
            for option in year_all_options:
              if counter == 1:
                option.click()
                break;
              counter = counter+1
          #搜尋今年1月
          if (month_arr[i] == 1 and i == 1):
            select_year = driver.find_element_by_name('yy')
            year_all_options = select_year.find_elements_by_tag_name("option")
            for option in year_all_options:
              if counter == 0:
                option.click()
                break;
              counter = counter + 1

          # 搜尋 前一個月 -> 現在這個月
          driver.find_element_by_link_text("查詢").click()

          #Delay
          time.sleep(1)

          #查詢這個月的 "結果訊息" 為何
          page = driver.page_source
          soup = BeautifulSoup(page)
          result_message = soup.find("div", {"id": "result-message"})
          print("Result Message :")
          if result_message.text:
            print(result_message.text)
          else:
            print("None!")

          # 判斷有無資料
          if result_message.text != u'查詢日期大於今日，請重新查詢!' and result_message.text != u'很抱歉，沒有符合條件的資料!':
            #抓取 Table 資料
            div = soup.find("div", {"class": "dataTables_wrapper no-footer"})
            table = div.find(lambda tag: tag.name == 'table')
            tbody = table.find('tbody')
            for row in tbody.find_all("tr"):
              data = row.find_all("td")
              One_Profile = []
              Date = data[0].find(text=True)
              oriOp = data[3].find(text=True)
              oriCl = data[6].find(text=True)
              oriFp = data[5].find(text=True)
              oriHp = data[4].find(text=True)
              if(oriOp == u'--'):
                continue
              newOp = ""
              newCl = ""
              newFp = ""
              newHp = ""
              for nch in range(len(oriOp)):
                if oriOp[nch] != u',':
                  newOp = newOp + oriOp[nch]
              for nch in range(len(oriCl)):
                if oriCl[nch] != u',':
                  newCl = newCl + oriCl[nch]
              for nch in range(len(oriFp)):
                if oriFp[nch] != u',':
                  newFp = newFp + oriFp[nch]
              for nch in range(len(oriHp)):
                if oriHp[nch] != u',':
                  newHp = newHp + oriHp[nch]
              One_Profile.append(Date)
              One_Profile.append(newOp)
              One_Profile.append(newCl)
              One_Profile.append(newFp)
              One_Profile.append(newHp)
              df.loc[len(df)] = One_Profile
        print("---> End to Get Data\n")
        # ---------------------------------------------------------------------------------------------------------------
        import MySQLdb
        # 取得 MySQL DataBase 資料
        try:
          Name_of_Table = self.ID_table[nID] + "_" + self.Name_table[nID]
          # 加入最新抓到的資料到 Mysql 指定 Table
          # 檢測方法 : 得到 DataBase 此 Table 最下面的資料
          #           若 月份 或 幾號 其中一個 > 最後一筆資料 加入一個陣列
          # 得到最後一筆
          final_data_month  = 0
          final_data_day    = 0
          sql = "SELECT * FROM " + Name_of_Table
          results = self.SELECT(sql)
          # 迴圈撈取資料
          # 顧慮到之前有92年，字串長度為8，之後為9，以後可能不同
          final = ""

          # 紀錄每日收盤
          cloArr = []

          for record in results:
            final             = record[0]
            r_l               = len(record[0])
            final_data_month  = int(record[0][r_l - 5:r_l - 3])
            final_data_day    = int(record[0][r_l - 2:])
            cloArr.append(float(record[2]))
          print("Final Data's is %s" % final )

          print("---> Start Add Data")
          print("***")
          # judge if add
          add_num  = 0
          for i in range(len(df)):
            data      = df.iloc[i][0]
            data_l    = len( data )
            # 判斷 db 裡是否有此資料,否則加入。
            if int( data[data_l - 5:data_l - 3] ) > final_data_month \
              or (int( data[data_l - 5:data_l - 3] ) == final_data_month and int( data[data_l - 2:] ) > final_data_day)\
              or ((int( data[data_l - 5:data_l - 3] ) == 1 and final_data_month == 12)):
              # Caculate MA
              cloArr.append(float(df.iloc[i][2]))
              cloLen = len(cloArr)
              MA3   = cloArr[cloLen-1]
              MA5   = cloArr[cloLen-1]
              MA10  = cloArr[cloLen-1]
              MA20  = cloArr[cloLen-1]
              MA60  = cloArr[cloLen-1]
              MA240 = cloArr[cloLen-1]
              if cloLen >= 3:
                MA3   = (np.average(cloArr[cloLen - 3:]))
              if cloLen >= 5:
                MA5   = (np.average(cloArr[cloLen - 5:]))
              if cloLen >= 10:
                MA10  = (np.average(cloArr[cloLen - 10:]))
              if cloLen >= 20:
                MA20  = (np.average(cloArr[cloLen - 20:]))
              if cloLen >= 60:
                MA60  = (np.average(cloArr[cloLen - 60:]))
              if cloLen >= 240:
                MA240 = (np.average(cloArr[cloLen - 240:]))
              # 取小數點後兩位
              new_MA3   = "%.2f" % MA3
              new_MA5   = "%.2f" % MA5
              new_MA10  = "%.2f" % MA10
              new_MA20  = "%.2f" % MA20
              new_MA60  = "%.2f" % MA60
              new_MA240 = "%.2f" % MA240
              # Insert
              sql = "INSERT INTO " + Name_of_Table + \
                    "(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice,MA3,MA5,MA10,MA20,MA60,MA240) values('" \
                    + df.iat[i, 0] + "','" + df.iat[i, 1] + "','" + df.iat[i, 2] + "','" + df.iat[i, 3] + "','" + df.iat[i, 4] + \
                    "','" + str(new_MA3) + "','" + str(new_MA5) + "','" + str(new_MA10) + \
                    "','" + str(new_MA20) + "','" + str(new_MA60) + "','" + str(new_MA240) + "')"
              self.INSERT(sql)
              add_num = add_num+1
          #判斷加入幾筆資料
          if add_num == 0:
            print("No Data Add!!!")
          else:
            print("Add %d Data!!!" % add_num)
          print("***")
          print("---> End to Add Data")
        except MySQLdb.Error as e:
          print "Error %d: %s" % (e.args[0], e.args[1])
      except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        print("**********************")
        print("   Reload Stock %d" % nID)
        print("**********************")
        nID = nID - 1
        #重跑一次 Get 此nID Stock
        # 關閉網站
        driver.quit()
        # 連上網站
        driver = webdriver.Chrome(self.Chrome_Driver_Path)
        driver.get(self.url_StockData)
    print("Updating END!!!\n\n")

    # 關閉網站
    driver.quit()

  # <---------- Test Function ---------->
  def Test_getFinalData_inDB(self):
    # 得到最後一筆
    final_data_month = 0
    final_data_day = 0
    sql = "SELECT * FROM " + self.ID_Table_Name
    # 執行SQL statement
    self.cursor.execute(sql)
    # 撈取多筆資料
    results = self.cursor.fetchall()
    # 迴圈撈取資料
    for record in results:
      final_data_month = int(record[0][4:6])
      final_data_day = int(record[0][7:])
    print("Final Data's DAta in %s , Month : %d , Day : %d" % (final_data_month, final_data_day))

  def __del__(self):
    self.db.close()
