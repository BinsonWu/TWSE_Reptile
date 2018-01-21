#coding=UTF-8

#為了解決中文比較問題
from __future__ import unicode_literals

from selenium import webdriver

from bs4 import BeautifulSoup
import pandas as pd

import MySQLdb

# Control Var
Chrome_Driver_Path  = "/usr/lib/chromium-browser/chromedriver"
url_ID              = "http://pchome.megatime.com.tw/search"
url_StockData       = "http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAYMAIN.php"
host                = ""
user                = ""
password            = ""
database            = ""


#得到ID
#EX 得到 台灣 '上市股' 的 全部股票的ID
def Get_all_TW_Listed_Shares_ID(ID_table,Name_table,select_Stock_Type):

    # Drive Chrome
    driver = webdriver.Chrome(Chrome_Driver_Path)
    driver.get(url_ID)

    stock_type          = driver.find_element_by_name('select1')
    stock_type_options  = stock_type.find_elements_by_tag_name("option")
    for option in stock_type_options:
        if option.text == select_Stock_Type.decode('utf-8'):
            option.click()

    #Press 確定
    button    = driver.find_element_by_xpath("//input[@value='　確 定　']")
    button.click()



    #抓到所有筆資料 (有好幾頁)
    #計算有幾頁
    div_pages   = driver.find_element_by_xpath("//div[@class='pages']")
    print("共有 %s 筆" % div_pages.text[22:25])
    n_page      = int(div_pages.text[22:25])/200 + 1
    print("共有 %d 頁" % n_page)

    #開始抓取ID
    print("----- Start to Get ID -----")
    for i in range(1,n_page+1,1):
        print("In Page %d :" % i)
        a = None
        if i != 1:
            print("page %s" % str(i))
            a       = driver.find_element_by_link_text(str(i))

        if a != None or i == 1:
            if a != None:
                a.click()
            page        = driver.page_source

            soup        = BeautifulSoup(page)

            div         = soup.find('div', id='stocks_list_table')
            table       = div.find(lambda tag: tag.name == 'table')
            tbody       = table.find('tbody')
            for row in tbody.find_all("tr"):
                data = row.find_all("td")
                if data:
                    #prevent list index out of range
                    for data_num in range(len(data)):
                        #print data[data_num].find(text=True),
                        getID = ""
                        getName = ""
                        for j in range( len(  data[data_num].find(text=True)  ) ):
                            if data[data_num].find(text=True)[j] == ' ':
                                break
                            getID   = getID + data[data_num].find(text=True)[j]
                        j=j+1
                        for k in range( j,len(  data[data_num].find(text=True)  ),1 ):
                            if data[data_num].find(text=True)[k] == '-':
                                break
                            getName   = getName + data[data_num].find(text=True)[k]

                        ID_table.append(getID)
                        Name_table.append(getName)
                        print("%12s %15s" % (getID, getName)),
                print ("")
        else:
            break
    print("----- End to Get ID -----")
    driver.quit()

#得到單支股票歷年資料
def Get_One_Stock_of_All_Data_to_Mysql(Which_Stock,Which_Table):
    # Create DataFrame
    df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

    # Drive Chrome
    driver = webdriver.Chrome(Chrome_Driver_Path)
    driver.get(url_StockData)
    search_input = driver.find_element_by_name('CO_ID')  # 取得搜尋框
    search_input.send_keys(Which_Stock)  # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

    # 得到selector
    # driver.find_element_by_name('query_year')
    # driver.find_element_by_name('query_month')

    # 得到selector每個options
    # select_year.find_elements_by_tag_name("option")
    # select_mouth.find_elements_by_tag_name("option")

    # 取得搜尋按鈕
    # driver.find_element_by_name('query-button').click()

    # 每刷新一次頁面element都要重新取得

    # 得到 幾年到幾年
    select_year = driver.find_element_by_name('query_year')
    year_all_options = select_year.find_elements_by_tag_name("option")

    newest_year = int(select_year.find_elements_by_tag_name("option")[0].text)
    earliest_year = 0
    for option in year_all_options:
        earliest_year = int(option.text)

    print earliest_year
    print newest_year
    print("----- Start to Get Data -----")
    # 利用 loop 把每個選項都跑過
    for i in range(earliest_year, newest_year + 1, 1):
        print("Year : %d" % i)
        select_year = driver.find_element_by_name('query_year')
        year_all_options = select_year.find_elements_by_tag_name("option")
        for option in year_all_options:
            if i == int(option.text):
                option.click()

        for j in range(1, 13, 1):
            print j
            select_month = driver.find_element_by_name('query_month')
            month_all_options = select_month.find_elements_by_tag_name("option")

            for option in month_all_options:
                if j == int(option.text):
                    option.click()

            # 令 chrome driver 按下 submit 觸發按鈕
            driver.find_element_by_name('query-button').click()

            page = driver.page_source
            soup = BeautifulSoup(page)
            div = soup.find('div', id='main-content')
            table = div.find(lambda tag: tag.name == 'table')
            tbody = table.find('tbody')
            for row in tbody.find_all("tr"):
                data = row.find_all("td")
                if data[0].find(text=True) != u'查無資料！':
                    One_Profile = []
                    One_Profile.append(data[0].find(text=True))
                    One_Profile.append(data[3].find(text=True))
                    One_Profile.append(data[6].find(text=True))
                    One_Profile.append(data[5].find(text=True))
                    One_Profile.append(data[4].find(text=True))
                    df.loc[len(df)] = One_Profile

    driver.quit()

    print("----- End to Get Data -----")

    print ("")
    print("DataFrame:")
    print df
    print ("")

    # 取得 MySQL DataBase 資料
    try:
        # 建立DB 連線資訊定設定中文編碼utf-8
        print("----- Start Add Data -----")
        db = MySQLdb.connect(host, user, password, database, charset='utf8')
        # 加入所有抓到的資料到Mysql 指定 Table
        # 先前成功的指令
        # INSERT INTO DataFrame(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('106/02/02','73.50','72.90','72.75','73.65');
        for i in range(len(df)):
            sql = "INSERT INTO " + Which_Table + "(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('" \
                  + df.iat[i, 0] + "','" + df.iat[i, 1] + "','" + df.iat[i, 2] + "','" + df.iat[i, 3] + "','" + df.iat[
                      i, 4] + "')"
            print sql
            # sql     = "INSERT INTO DataFrame(Date, OpeningPrice, ClosingPrice, FloorPrice, HighestPrice) values('106/02/02', '73.50', '72.90', '72.75', '73.65')"
            cursor = db.cursor()
            cursor.execute(sql)  # 執行指令
            db.commit()
        print("----- End to Add Data -----")

        print("----- Check Table:DataFrame Data -----")
        sql = "SELECT * FROM DataFrame"
        # 執行SQL statement
        cursor = db.cursor()
        cursor.execute(sql)  # 執行指令
        # 撈取多筆資料
        results = cursor.fetchall()
        # 迴圈撈取資料
        for record in results:
            col1 = record[0]
            col2 = record[1]
            col3 = record[2]
            col4 = record[3]
            col5 = record[4]
            print "%s, %s, %s, %s, %s" % (col1, col2, col3, col4, col5)
        print("----- Check Over -----")

        # 關閉連線
        db.close()

    except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])

#得到所有股票歷年資料
def Get_All_Stock_of_All_Data_to_Mysql(ID_table,Name_table):
    #連上網站
    driver = webdriver.Chrome(Chrome_Driver_Path)
    driver.get(url_StockData)

    #依 ID_Table 第0支股票開始
    for nID in range(827,len(ID_table),1):
	try:
		print("\n<--------------------------->")
		print("Get Stock %d : %s_%s " % (nID,ID_table[nID],Name_table[nID]))
		#Set Which Stock
		Which_Stock     = ID_table[nID]

		# Create DataFrame
		df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

		# Drive Chrome Input Which Stock ID We Want
		search_input = driver.find_element_by_name('CO_ID')     # 取得搜尋框
		search_input.clear()                                    # 清空資料
		search_input.send_keys(Which_Stock)                     # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

		# 得到 幾年到幾年
		select_year         = driver.find_element_by_name('query_year')
		year_all_options    = select_year.find_elements_by_tag_name("option")

		newest_year         = int(select_year.find_elements_by_tag_name("option")[0].text)
		earliest_year       = 0
		for option in year_all_options:
		    earliest_year   = int(option.text)

		#print("Search From %s to %s" % (earliest_year,newest_year))

		print("----- Start to Get Data -----")
		# 利用 loop 把每個選項都跑過 即 '每年' '每月'
		for i in range( earliest_year, newest_year + 1 , 1):
		    #print("Year : %d" % i)
		    select_year         = driver.find_element_by_name('query_year')
		    year_all_options    = select_year.find_elements_by_tag_name("option")
		    for option in year_all_options:
		        if i == int(option.text):
		            option.click()

		    for j in range(1,13,1):
		        #print j
		        select_month = driver.find_element_by_name('query_month')
		        month_all_options = select_month.find_elements_by_tag_name("option")

		        for option in month_all_options:
		            if j == int(option.text):
		                option.click()

		        # 令 chrome driver 按下 submit 觸發按鈕
		        driver.find_element_by_name('query-button').click()

		        page = driver.page_source
		        soup = BeautifulSoup(page)
		        div = soup.find('div', id='main-content')
		        table = div.find(lambda tag: tag.name == 'table')
		        tbody = table.find('tbody')
		        for row in tbody.find_all("tr"):
		            data = row.find_all("td")
		            if data[0].find(text=True) != u'查無資料！':
		                One_Profile = []
		                One_Profile.append(data[0].find(text=True))
		                One_Profile.append(data[3].find(text=True))
		                One_Profile.append(data[6].find(text=True))
		                One_Profile.append(data[5].find(text=True))
		                One_Profile.append(data[4].find(text=True))
		                df.loc[len(df)] = One_Profile
		print("----- End to Get Data -----")


		#---------------------------------------------------------------------------------------------------------------


		import MySQLdb
		# 取得 MySQL DataBase 資料
		try:
		    # 建立DB 連線資訊定設定中文編碼utf-8
		    db = MySQLdb.connect(host, user, password, database, charset='utf8')

		    print("----- Start Add Data -----")
		    # Create This Stock Table
		    Name_of_Table = ID_table[nID] + "_" + Name_table[nID]
		    sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null,FloorPrice float not null,HighestPrice float not null)character set = utf8"
		    #print sql
		    cursor = db.cursor()
		    cursor.execute(sql)  # 執行指令

		    # 加入所有抓到的資料到Mysql 指定 Table ( 沒有table就創一個 )# INSERT INTO DataFrame(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('106/02/02','73.50','72.90','72.75','73.65');
		    for i in range(len(df)):
		        #Insert
		        sql = "INSERT INTO " + Name_of_Table + "(Date,OpeningPrice,ClosingPrice,FloorPrice,HighestPrice) values('" \
		              + df.iat[i, 0] + "','" + df.iat[i, 1] + "','" + df.iat[i, 2] + "','" + df.iat[i, 3] + "','" + df.iat[
		                  i, 4] + "')"
		        #print sql
		        # sql     = "INSERT INTO DataFrame(Date, OpeningPrice, ClosingPrice, FloorPrice, HighestPrice) values('106/02/02', '73.50', '72.90', '72.75', '73.65')"
		        cursor = db.cursor()
		        cursor.execute(sql)  # 執行指令
		        db.commit()
		    print("----- End to Add Data -----")

		    # 關閉連線
		    db.close()

		except MySQLdb.Error as e:
		    print "Error %d: %s" % (e.args[0], e.args[1])
	except:
		print("Reload : %d" % nID)
		nID = nID - 1
		driver.quit()
		driver = webdriver.Chrome(Chrome_Driver_Path)
    		driver.get(url_StockData)

    #關閉網站
    driver.quit()

#ID & Name Add to MySQL
def Add_ID_to_Mysql(ID_table,Name_table):
    # Insert To DataBase
    db = MySQLdb.connect(host, user, password, database, charset='utf8')
    cursor = db.cursor()

    # 加入所有抓到的資料到Mysql 指定 Table
    for i in range(len(ID_table)):
        sql = "INSERT INTO Stock_ID_Name(ID,Name) values('" \
              + ID_table[i] + "','" + Name_table[i] + "')"
        print sql
        cursor.execute(sql)  # 執行指令
        db.commit()

#Test the Order if Succeed
def test_sql(ID_table,Name_table):
    db = MySQLdb.connect(host, user, password, database, charset='utf8')
    Name_of_Table = ID_table[0] + "_" + Name_table[0]
    sql = "create table " + Name_of_Table + "(Date varchar(20),OpeningPrice float not null,ClosingPrice float not null,FloorPrice float not null,HighestPrice float not null)character set = utf8"
    print sql
    cursor = db.cursor()
    cursor.execute(sql)  # 執行指令

#Test Chrome Change Stock if Succeed
def test_change_stock(ID_table,Name_table):
    driver = webdriver.Chrome(Chrome_Driver_Path)
    driver.get(url_StockData)

    # 依 ID_Table 第0支股票開始
    for nID in range(len(ID_table)):
	try:
		print("\n<--------------------------->")
		print("Get Stock %d : %s_%s " % (nID, ID_table[nID], Name_table[nID]))
		# Set Which Stock
		Which_Stock = ID_table[nID]

		# Create DataFrame
		df = pd.DataFrame(columns=['Date', 'Opening price', 'Closing Price', 'Floor Price', 'Highest Price'])

		search_input = driver.find_element_by_name('CO_ID')     # 取得搜尋框
		search_input.clear()                                    # 清空
		# Drive Chrome Input Which Stock ID We Want
		search_input.send_keys(Which_Stock)                     # 在搜尋框內輸入 '哪支股票' 得到此股票的資訊

		# 得到 幾年到幾年
		select_year = driver.find_element_by_name('query_year')
		year_all_options = select_year.find_elements_by_tag_name("option")

		newest_year = int(select_year.find_elements_by_tag_name("option")[0].text)
		earliest_year = 0
		for option in year_all_options:
		    earliest_year = int(option.text)

		print earliest_year
		print newest_year
		print("----- Start to Get Data -----")
		# 利用 loop 把每個選項都跑過
		for i in range(newest_year, newest_year + 1, 1):
		    print("Year : %d" % i)
		    select_year = driver.find_element_by_name('query_year')
		    year_all_options = select_year.find_elements_by_tag_name("option")
		    for option in year_all_options:
		        if i == int(option.text):
		            option.click()

		    for j in range(1, 13, 1):
		        print j
		        select_month = driver.find_element_by_name('query_month')
		        month_all_options = select_month.find_elements_by_tag_name("option")

		        for option in month_all_options:
		            if j == int(option.text):
		                option.click()

		        # 令 chrome driver 按下 submit 觸發按鈕
		        driver.find_element_by_name('query-button').click()
	except:
		print("Reload:Stock %d" % nID)
		nID = nID - 1

    driver.quit()

#Delete Table Except 'Stock_ID_Name'
def drop_table_except_Stock_ID_Name(ID_table,Name_table):
    db = MySQLdb.connect(host, user, password, database, charset='utf8')

    for nID in range( len(ID_table) ):
        Name_of_Table   = ID_table[nID] + "_" + Name_table[nID]
        print Name_of_Table
        sql             = "drop table " + Name_of_Table
        print sql
        cursor = db.cursor()
        cursor.execute(sql)  # 執行指令
