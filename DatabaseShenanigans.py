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
finances_db=Config.Finances.fullpath

#------- Incantations end here -------------------------------------------------

#Layouts
def menu():
    #Get list of common products from DB
    products=GetProducts()
    listofproducts=[]
    for product in products:
        listofproducts.append(product[0]+"("+str(product[2])+")")

    lout=[  #text and button stuff
            [sg.Text('Pick desired graph')],
            [sg.Button('TopTypeMonthly'), 
                sg.Button('Most common products'),
                sg.Button('Income'),
                sg.Button('Monthly Bilance'),
            ],
            [sg.Text('Product'),
                sg.DropDown(listofproducts),
                sg.Button('Product')],
            [sg.Canvas(key='canvas',                size=(Config.plot_width, Config.plot_height-160), expand_x=True, expand_y=True)],
            [sg.Button('Exit'),
                sg.Button('Clear')]  
        ]
    return lout

#Database stuff
def getfromdb(database, select):
    connection = sqlite3.connect(database)  #<TODO>Try this, repeat if connection fails
    cursor = connection.cursor()
    cursor.execute(select)
    rows=cursor.fetchall()
    connection.close()
    return rows
def Get_collection_fromdb(database, select_template, conditions):
    #select use [CONDITION] as placeholder for condition 
    datasets=[]
    select=''
    for condition in conditions:
        select=select_template.replace(Config.placeholder,condition)
        data_from_db=getfromdb(database,select)
        datasets.append((data_from_db, condition))
    return datasets

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
def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def GetProducts():
    get_products=   Config.Finances.selects['ProductSummary']
    return getfromdb(finances_db, get_products)
def Income():
    income= Get_collection_fromdb(finances_db, 
                                  Config.placeholder, 
                                  {Config.Finances.selects["MonthlyIncome"]})
    return Prepare_plot(income, 'Monthly income')
def Monthly_Bilance():
    tables=('MonthlyIncome','MonthlyBills','MonthlyExpenditures')
    bilance=Get_collection_fromdb(finances_db,
                                  Config.Finances.selects['AnyTable'],
                                  tables)
    return Prepare_plot(bilance, 'Bilance')
def TopTypeMonthly():
    top_type= getfromdb(finances_db, 
                        Config.Finances.selects['MostCommonProduct'])[0][0]        #Access value directly
    type_monthly= Config.Finances.selects['TypeSummary'].replace(Config.placeholder, top_type) #replace placeholder while using
    top_type_monthly= Get_collection_fromdb(finances_db, 
                                            Config.placeholder, 
                                            {type_monthly})
    top_type_monthly=[(top_type_monthly[0][0], top_type)]  #Changing Select to type
    return Prepare_plot(top_type_monthly, top_type+' products across time')
def GivenProduct(Product):
    product_monthly=Config.Finances.selects['GivenProduct']
    product_stats=Get_collection_fromdb(finances_db, product_monthly, {Product})
    return Prepare_plot(product_stats, Product)
def MostCommonProducts():
    product_monthly=Config.Finances.selects['GivenProduct']
    all_products= GetProducts()
    product_list=[product[0] for product in all_products[0:Config.limit]]
    products= Get_collection_fromdb(finances_db, 
                                    product_monthly, 
                                    product_list)
    return Prepare_plot(products, 'Products')

def main():
    sg.theme('DarkAmber')
    layout = menu();
    prevlayout = [];
    
    window = sg.Window('Budgeter', 
                    layout, 
                    size=(Config.window_width, Config.window_height),
                    auto_size_buttons=False,
                    default_button_element_size=(Config.btn_width, Config.btn_height),
                    #TODO: fix, icon source: https://www.iconpacks.net/free-icon/money-bag-6384.html
                    titlebar_icon="E:\Downloads\money-bag-6384_1_.ico",
                    finalize=False
                    )
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):	
            break
        if event in ('Most common products'):
            draw_figure(window['canvas'].TKCanvas, MostCommonProducts())
            continue
        if event in ('Income'):
            draw_figure(window['canvas'].TKCanvas, Income())
        if event in ('Monthly Bilance'):
            draw_figure(window['canvas'].TKCanvas, Monthly_Bilance()) 
            continue
        if event in ('TopTypeMonthly'):
            draw_figure(window['canvas'].TKCanvas, TopTypeMonthly())
            continue
        if event in ('Product'):
            product=values[0]
            draw_figure(window['canvas'].TKCanvas, GivenProduct(product.partition("(")[0]))
            continue
        if event in ('Clear'):
            #TODO: Clear plot before drawing next
            print('window[\'canvas\'].TKCanvas.delete("all") does not work')
            continue
    window.close()

if __name__ == "__main__":
    main()