# coding=UTF-8
from Db_Auto import DBConn

try:
  dbuse = DBConn()

  dbuse.dbConnect()

  # 建立insert statement 並呼叫runInsert function
  sql = "INSERT INTO DataFrame(Date, OpeningPrice, ClosingPrice, FloorPrice, HighestPrice) VALUES('106/02/02', '73.50', '72.90', '72.75', '73.65')"
  dbuse.runInsert(sql)

  dbuse.dbClose()
except:
  print "MySQL DB Error"