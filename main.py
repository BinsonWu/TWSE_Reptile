# coding=UTF-8
import FunctionLib



if __name__ == '__main__':

    #print("%s" % u'我')

    #getID
    ID_table    = []
    Name_table  = []
    select_Stock_Type  = '上市股'
    FunctionLib.Get_all_TW_Listed_Shares_ID(ID_table,Name_table,select_Stock_Type)

    #Add_ID_to_Mysql
    #FunctionLib.Add_ID_to_Mysql(ID_table,Name_table)

    '''
    #Get All Data of One Stock
    Which_Stock         = '0050' #ID_table[0]
    Which_Table         = '0050_元大台灣50'
    FunctionLib.Get_One_Stock_of_All_Data_to_Mysql(Which_Stock,Which_Table)
    '''


    #Get All Data of All Stock
    FunctionLib.Get_All_Stock_of_All_Data_to_Mysql(ID_table,Name_table)

    #FunctionLib.test_sql(ID_table, Name_table)

    #Test Change Stock
    #FunctionLib.test_change_stock(ID_table,Name_table)

    #Drop Table Except Stock_ID_Name
    #FunctionLib.drop_table_except_Stock_ID_Name(ID_table,Name_table)