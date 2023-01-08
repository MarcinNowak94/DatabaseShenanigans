#pip install matplotlib first y'all via: python -m pip install -U matplotlib
#https://stackabuse.com/converting-strings-to-datetime-in-python/
#https://matplotlib.org/gallery/style_sheets/fivethirtyeight.html#sphx-glr-gallery-style-sheets-fivethirtyeight-py
#https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py
import sqlite3
import time
import datetime
import base64
import PySimpleGUI as sg
import pandas

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')         #Use tinker to integrate matplotlib with GUI
from dateutil import parser

import Config
#placeholder=Config.placeholder
#finances_db=Config.databases[0]['fullpath']



#Database stuff
def getfromdb(database, select):
    connection = sqlite3.connect(database)  #<TODO>Try this, repeat if connection fails
    cursor = connection.cursor()
    cursor.execute(select)
    rows=cursor.fetchall()
    connection.close()
    return rows
def Get_collection_fromdb(database, select_template, conditions):
    #select use [R_CONDITION] as placeholder for condition 
    datasets=[]
    select=''
    for condition in conditions:
        select=select_template.replace(Config.placeholder,condition)
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
    print('Above line produces goes int infinite loop')
    return
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
    plt.show(figure)
    
    return
def Prepare_plot(set, title):
    plt.style.use('fivethirtyeight')
    figure, ax = plt.subplots()    #fig=figure, ax=axes object on figure
    for data in set:
        dates=[]
        values=[]
        for record in data[0]:
            dates.append(parser.parse(record[0]))
            values.append(record[1])
        ax.plot(dates,values, label=data[1])
    ax.set_title(str(title))
    ax.legend()

    fig = plt.gcf()      # if using Pyplot then get the figure from the plot
    return fig
""" 
#Visualizatins
def Monthly_Bilance():
    get_bilance=(Finances.selects['Income'],
                 Finances.selects['Bills'],
                 Finances.selects['MonthlyExpenditures'])
    bilance=Get_collection_fromdb(Finances.fullpath, placeholder, get_bilance)
    Visualize_set(bilance, 'Bilance')
def Income():
    income=     Get_collection_fromdb(Finances.fullpath, placeholder, Finances.selects['Income'])
    Visualize_set(income, 'Monthly income')
def MostCommonProducts():
    get_products=   Finances.selects["Products"]
    product_monthly=Config.databases[0]['select'][5]
    
    all_products=   getfromdb(finances_db, get_products)
    product_list=[product[0] for product in all_products[0:Config.limit]]
    products=       Get_collection_fromdb(finances_db, product_monthly, product_list)

    Visualize_set(products, 'Products')
    return
def GivenProduct(Product):
    product_monthly=Config.databases[0]['select'][5].replace(placeholder, Product)
    product_stats=getfromdb(finances_db, product_monthly)
    Visualize(product_stats, Product)
    return
def TopTypeMonthly():
    top_type= getfromdb(finances_db, Config.databases[0]['select'][2])[0][0]        #Access value directly
    type_monthly=   Config.databases[0]['select'][3].replace(placeholder, top_type) #replace placeholder while using
    top_type_monthly= getfromdb(finances_db, type_monthly)
    Visualize(top_type_monthly, top_type+' products across time')

def GetFullSchema():
    get_tables= Config.select_common[0]             #replace placeholder while using
    get_columns=Config.select_common[2]         #replace placeholder while using
    tables=     getfromdb(finances_db, get_tables)        
    for table in tables:
        columnsinfo=get_columns.replace(placeholder, table[1])
        columns=getfromdb(finances_db, columnsinfo)
        print(columns)
    print("<TODO> Not finished yet!\a")
    return

def Monthly_Bilance_GUI():
    get_bilance=(Config.databases[0]['select'][6],
                 Config.databases[0]['select'][7],
                 Config.databases[0]['select'][8])
    bilance=Get_collection_fromdb(finances_db, placeholder, get_bilance)
    return Prepare_plot(bilance, 'Bilance')

def MostCommonProducts_GUI():
    get_products=   Config.databases[0]['select'][4]
    product_monthly=Config.databases[0]['select'][5]
    
    all_products=   getfromdb(finances_db, get_products)
    product_list=[product[0] for product in all_products[0:Config.limit]]
    products=       Get_collection_fromdb(finances_db, product_monthly, product_list)

    return Prepare_plot(products, 'Products')
def GivenProduct_GUI(Product):
    product_monthly=Config.databases[0]['select'][5]
    product_stats=Get_collection_fromdb(finances_db, product_monthly, {Product})
    return Prepare_plot(product_stats, Product)
def TopTypeMonthly_GUI():
    top_type= getfromdb(finances_db, Config.databases[0]['select'][2])[0][0]        #Access value directly
    type_monthly=   Config.databases[0]['select'][3].replace(placeholder, top_type) #replace placeholder while using
    top_type_monthly= Get_collection_fromdb(finances_db, placeholder, {type_monthly})
    top_type_monthly=[(top_type_monthly[0][0], top_type)]                           #Changing Select to type
    return Prepare_plot(top_type_monthly, top_type+' products across time')
def MonthlyCharge_GUI():
    charge=Get_collection_fromdb(finances_db, placeholder, {databases[0].selects(MonthlyCharge)})
    return Prepare_plot(charge, "Monthly charge rate calculation")
"""
def Income_GUI():
    income= Get_collection_fromdb(Config.Finances.fullpath, 
                                  Config.placeholder, 
                                  {Config.Finances.selects["MonthlyIncome"]})
    return Prepare_plot(income, 'Monthly income')


#Prepared selects
#get_views=      Config.select_common[1]             #replace placeholder during usage

# GetFullSchema()
# TopTypeMonthly()
# MostCommonProducts()    
#Income()
# Monthly_Bilance()
# MonthlyCharge()
# GivenProduct('Fryzjer')

def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def preparelayout():
    #Previous version
    lout=[  #text and button stuff
                [sg.Text('Pick desired graph')],
                [sg.Button('TopTypeMonthly',        size=(Config.btn_width, Config.btn_height)), 
                 sg.Button('Most common products',  size=(Config.btn_width, Config.btn_height)),
                 sg.Button('Income',                size=(Config.btn_width, Config.btn_height)),
                 sg.Button('Monthly Bilance',       size=(Config.btn_width, Config.btn_height)),
                 sg.Button('MonthlyCharge',         size=(Config.btn_width, Config.btn_height))],
                [sg.Text('Product',                 size=(Config.btn_width, Config.btn_height)),
                 sg.InputText(),
                 sg.Button('Product',               size=(Config.btn_width, Config.btn_height))],
                [sg.Canvas(key='canvas',            size=(Config.plot_width, Config.plot_height))],
                [sg.Button('Exit',                  size=(Config.btn_width, Config.btn_height )),
                 sg.Button('Clear',                 size=(Config.btn_width, Config.btn_height))]  
            ]
    return lout

def main():
    sg.theme('DarkAmber')	# Add a touch of color

    #for Select in Finances.selects

    # All the stuff inside your window.
    layout = preparelayout();

    # Create the Window
    window = sg.Window('Finance visualizer', 
                    layout, 
                    size=(Config.window_width, Config.window_height),
                    finalize=True)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):	
            break
        """
        if event in ('TopTypeMonthly'):
            draw_figure(window['canvas'].TKCanvas, TopTypeMonthly_GUI())
            continue
        if event in ('Most common products'):
            draw_figure(window['canvas'].TKCanvas, MostCommonProducts_GUI())
            continue
        if event in ('Income'):
            draw_figure(window['canvas'].TKCanvas, Income_GUI())
            continue
        if event in ('Monthly_Bilance'):
            draw_figure(window['canvas'].TKCanvas, Monthly_Bilance_GUI()) 
            continue
        if event in ('MonthlyCharge'):
            draw_figure(window['canvas'].TKCanvas, MonthlyCharge_GUI())
            continue
        if event in ('Product'):
            product=values[0]
            draw_figure(window['canvas'].TKCanvas, GivenProduct_GUI(product))
            continue
        """
        if event in ('Income'):
            draw_figure(window['canvas'].TKCanvas, Income_GUI())
        if event in ('Clear'):
            #TODO: Clear plot before drawing next
            print('window[\'canvas\'].TKCanvas.delete("all") does not work')
            continue
    window.close()

if __name__ == "__main__":
    main()