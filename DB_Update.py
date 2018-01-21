#coding=UTF-8
import Db_Auto

UpdateS = Db_Auto.DataBase_Service()

select_Stock_Type = '上市股'
UpdateS.Update_ID_Table(select_Stock_Type)                             #更新 DataBase內的 Stock_ID_Name 可能有新增減少股票
UpdateS.Update_Stock_Data()

#UpdateS.getTW_oneTypeStock_All_ID(select_Stock_Type)                   #得到 '上市股' 所有 ID & Name

'''Table_Name      = 'Stock_ID_Name'
Column_Name     = 'Record_Low'
Column_Type     = 'float not null'
#UpdateS.Add_Table_Column(Table_Name,Column_Name,Column_Type)'''


'''Column_Name     = 'DayAve'
Column_Type     = 'float not null'
UpdateS.Add_allStockTable_Column(Column_Name,Column_Type)'''

'''Which_Stock = "3008"
Which_Table = "3008_大立光"
UpdateS.getOne_Stock_All_Data_to_Mysql(Which_Stock,Which_Table)'''

'''select_Stock_Type = '上市股'
UpdateS.getTW_oneTypeStock_All_ID(select_Stock_Type)
UpdateS.Add_All_ID_to_Mysql()'''

#UpdateS.getAll_Stock_All_Data_to_Mysql()

#UpdateS.Set_All_MA()

#UpdateS.getAllCashDividedData()