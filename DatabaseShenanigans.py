#pip install matplotlib first y'all via: python -m pip install -U matplotlib
#https://stackabuse.com/converting-strings-to-datetime-in-python/
#https://matplotlib.org/gallery/style_sheets/fivethirtyeight.html#sphx-glr-gallery-style-sheets-fivethirtyeight-py
import sqlite3
import time
import datetime
import base64
import Config

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser

placeholder=Config.placeholder
finances_db=Config.databases[0]['fullpath']

#Database stuff
def create_query(columns, table, modifier, ):
    select='SELECT '+columns+' FROM '+table+' '+modifier
    return select
def getfromdb(database,select):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(select)
    rows=cursor.fetchall()
    conn.close()
    return rows
def Get_collection_fromdb(database, select_template, conditions):
    #select use [R_CONDITION] as placeholder for condition 
    datasets=[]
    select=''
    for condition in conditions:
        select=select_template.replace(placeholder,condition)
        print(select)
        data_from_db=getfromdb(database,select)
        datasets.append((data_from_db, condition))
    return datasets

#Graphing
def Visualize(data, title):
    dates=[]
    values=[]
    for record in data:
        dates.append(parser.parse(record[0]))    
        values.append(record[1])
    plt.style.use('fivethirtyeight')
    figure, ax = plt.subplots()    #figure, ax=axes object on figure
    ax.plot(dates,values)
    ax.set_title(str(title))    
    plt.show(figure)
def Visualize_set(set, title):
    plt.style.use('fivethirtyeight')
    figure, ax = plt.subplots()    #fig=figure, ax=axes object on figure
    for data in set:
        dates=[]
        values=[]
        for record in data[0]:
            dates.append(parser.parse(record[0]))    
            values.append(record[1])
        ax.plot(dates,values, label=data[1])
        #Anootating as per: https://stackoverflow.com/questions/6282058/writing-numerical-values-on-the-plot-with-matplotlib
        #for point in data[0]:
        #    print(point)
        #    ax.annotate(point[1], point)
        #https://python-graph-gallery.com/123-highlight-a-line-in-line-plot/ - annotating

    ax.set_title(str(title))
    ax.legend()
    plt.show()

#Visualizatins
def Monthly_Bilance():
    get_bilance=(Config.databases[0]['select'][6],
                 Config.databases[0]['select'][7],
                 Config.databases[0]['select'][8])
    bilance=Get_collection_fromdb(finances_db, placeholder, get_bilance)
    Visualize_set(bilance, 'Bilance')
def Methods():
    database=Config.databases[1]['fullpath']
    methods=getfromdb(database, Config.databases[1]['select'][0])
    method_list=[method[0] for method in methods]
    methods_to_graph=Get_collection_fromdb(database, Config.databases[1]['select'][1], method_list)
    Visualize_set(methods_to_graph, 'Methods')
def Income():
    get_income= Config.databases[0]['select'][1]
    income=     getfromdb(finances_db, get_income)
    Visualize(income, 'Monthly income')
def MostCommonProducts():
    get_products=   Config.databases[0]['select'][4]
    product_monthly=Config.databases[0]['select'][5]
    
    all_products=   getfromdb(finances_db, get_products)
    product_list=[product[0] for product in all_products[0:Config.limit]]
    products=       Get_collection_fromdb(finances_db, product_monthly, product_list)

    Visualize_set(products, 'Products')
def TopTypeMonthly():
    top_type= getfromdb(finances_db, Config.databases[0]['select'][2])[0][0]        #Access value directly
    type_monthly=   Config.databases[0]['select'][3].replace(placeholder, top_type) #replace placeholder while using
    top_type_monthly= getfromdb(finances_db, type_monthly)
    Visualize(top_type_monthly, top_type+' products across time')
def GetFullSchema():
    get_tables= Config.select_common[0]             #replace placeholder while using
    get_columns=    Config.select_common[2]         #replace placeholder while using
    tables=     getfromdb(finances_db, get_tables)        
    for table in tables:
        columnsinfo=get_columns.replace(placeholder, table[1])
        columns=getfromdb(finances_db, columnsinfo)
        print(columns)
    print("<TODO> Not finished yet!\a")


#Prepared selects
get_views=      Config.select_common[1]             #replace placeholder while using

GetFullSchema()
TopTypeMonthly()
MostCommonProducts()    
Income()
Bilance()
