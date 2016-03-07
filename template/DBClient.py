# coding=gbk

import pyodbc

database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=115.28.63.225;DATABASE=pachong;UID=likai;PWD=LiKai0129')
# database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=LENOVO-LK\MSSQL;DATABASE=pachong;UID=sa;PWD=LiKai0129')
database_client_cursor = database_client_connection.cursor()


