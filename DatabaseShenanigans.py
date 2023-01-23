# Required package to install
# pip install matplotlib first y'all via: python -m pip install -U matplotlib

#https://stackabuse.com/converting-strings-to-datetime-in-python/
#https://matplotlib.org/gallery/style_sheets/fivethirtyeight.html#sphx-glr-gallery-style-sheets-fivethirtyeight-py
#https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py
import sqlite3
import time
import datetime
import base64
import PySimpleGUI as sg    #Naming convention recommended by the author
import pandas
from enum import Enum

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')         #Use tinker to integrate matplotlib with GUI
from dateutil import parser

import Config
finances_db=Config.Finances.fullpath
visibleelement=Config.startlayout
#------- Incantations end here -------------------------------------------------

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
def GetDBInfo(database):
    db={}
    for table in getfromdb(database, Config.Common['GetTables']):
        table=table[0] #Get only text
        select=Config.Common['GetColumns'].replace(Config.placeholder, table)
        columns=getfromdb(database, select)
        names=[]
        for values in columns:
            names.append(values[0])
        db[table]={"name": table, "columns": names}
    return db
schema=GetDBInfo(finances_db)

#Visualizations
def Prepare_plot(set, title):
    plt.style.use('fivethirtyeight')
    figure, axes = plt.subplots()    #fig=figure, ax=axes object on figure
    for data in set:
        dates=[]
        values=[]
        for record in data[0]:
            dates.append(parser.parse(record[0]))
            values.append(record[1])
        axes.plot(dates,values, label=data[1])
    axes.set_title(str(title))
    axes.legend()

    #fig = plt.gcf()      # if using Pyplot then get the figure from the plot
    return figure
def draw_figure(canvas, figure, loc=(0, 0)):
    #Clear canvas as per https://stackoverflow.com/questions/64403707/interactive-matplotlib-plot-in-pysimplegui
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    #Draw new figure
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(fill='both', expand=True)
    return figure_canvas_agg

def IncomeSummary():
    income= Get_collection_fromdb(finances_db, 
                                  Config.placeholder, 
                                  {Config.Finances.selects["MonthlyIncome"]})
    return Prepare_plot(income, 'Monthly income')
def MonthlyBilance():
    tables=('MonthlyIncome','MonthlyBills','MonthlyExpenditures')
    bilance=Get_collection_fromdb(finances_db,
                                  Config.Finances.selects['AnyTable'],
                                  tables)
    return Prepare_plot(bilance, 'Bilance')
def TopTypeMonthly():
    top_type= getfromdb(finances_db, 
                        Config.Finances.selects['MostCommonProduct'])[0][0]        #Access value directly
    type_monthly= Config.Finances.selects['GivenType'].replace(Config.placeholder, top_type) #replace placeholder while using
    top_type_monthly= Get_collection_fromdb(finances_db, 
                                            Config.placeholder, 
                                            {type_monthly})
    top_type_monthly=[(top_type_monthly[0][0], top_type)]  #Changing Select to type
    return Prepare_plot(top_type_monthly, top_type+' products across time')
def GivenProduct(Product):
    product_monthly=Config.Finances.selects['GivenProduct']
    product_stats=Get_collection_fromdb(finances_db, product_monthly, {Product})
    return Prepare_plot(product_stats, Product)
def GivenType(type):
    type_monthly=Config.Finances.selects['GivenType']
    type_stats=Get_collection_fromdb(finances_db, type_monthly, {type})
    return Prepare_plot(type_stats, type)
def MostCommonProducts(amount):
    product_monthly=Config.Finances.selects['GivenProduct']
    all_products= Listfromtable("ProductSummary")
    product_list=[product[0] for product in all_products[0:amount]]
    products= Get_collection_fromdb(finances_db, 
                                    product_monthly, 
                                    product_list)
    return Prepare_plot(products, 'Products')

#Layout and menu ---------------------------------------------------------------
def Listfromtable(table, addvalues=True):
    #Get list of common products from DB
    values=getfromdb(finances_db, Config.Finances.selects[table])
    valuelist=[]
    
    for value in values:
        element = value[0]+"("+str(value[2])+")" if addvalues else value[0]
        valuelist.append(element)
    return valuelist
def TableToLayout(table, tables, visible=True):
    select=Config.Finances.selects['AnyTable']
    select=select.replace(Config.placeholder, tables[table]['name'])
    vals=getfromdb(finances_db, select)
    tableelement=sg.Table(key=tables[table]['name']+'_table',
                        values=vals,
                        headings=tables[table]['columns'],
                        auto_size_columns=True,
                        expand_x=True, 
                        expand_y=True,
                        visible=True,
                        enable_click_events=True)   #Allows selection
    return tableelement
def GenerateTableEditor(table):
    global schema
    editor=[ [sg.Text(table+' Editor'), 
             sg.Button(key=table+'Import',
                    button_text='Import data',
                    tooltip='Import data from properly formatted CSV file. Example provided in resources directory.')],
            [TableToLayout(table, schema)]]
    return editor
def ChangeLayout(window, element):
    global visibleelement
    window[visibleelement].update(visible=False)
    visibleelement=element
    window[visibleelement].update(visible=True)

def main():
    #layout preparation
    products=Listfromtable("ProductSummary")
    types=Listfromtable("TypeSummary")
    sg.theme('DarkAmber')
    menu = [['Visualizations', 
                ['Most common products', 
                 'Income summary',
                 'Monthly Bilance',
                 'TopTypeMonthly',
                 'Type'
                    ,[types],
                 'Product'
                    ,[products]]],
            ['Insert data',                     #TODO
                ['Expenditures',                #TODO
                 'Bills',                       #TODO
                 'Income',                      #TODO
                 'Types' ,                      #TODO
                 'Products',                    #TODO
                 'Miscelaneous',]],             #TODO
            ['Options',                         #TODO
                ['Configure',                   #TODO
                'About...']]                    #TODO
            ]

    Visualization=[ [sg.Text('Visualizations')],
                    [sg.Canvas(key='canvas',
                        size=(Config.plot_width, Config.plot_height-160),
                        expand_x=True, 
                        expand_y=True,
                        visible=True)]]
    IncomeEdition=GenerateTableEditor('Income')
    ExpendituresEdition=GenerateTableEditor('Expenditures')
    BillsEdition=GenerateTableEditor('Bills')
    TypesEdition=GenerateTableEditor('ProductTypes')
    ProductsEdition=GenerateTableEditor('Products')
    MiscelaneousEdition=[[sg.Text('Miscelaneous Editor')],
                        [sg.Button(key='AddType', 
                                    button_text="Add type",
                                    tooltip="Adds type of products to database")]]
    
    #Inspired by DEMO https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Column_Elem_Swap_Entire_Window.py
    layout=[
        [sg.Menu(key='Menu', menu_definition=menu)],
        [sg.Column(Visualization, visible=False, key='Visualization', expand_x=True, expand_y=True), 
         sg.Column(IncomeEdition, visible=False, key='IncomeEdition', expand_x=True, expand_y=True), 
         sg.Column(ExpendituresEdition, visible=False, key='ExpendituresEdition', expand_x=True, expand_y=True),
         sg.Column(BillsEdition, visible=False, key='BillsEdition', expand_x=True, expand_y=True),
         sg.Column(MiscelaneousEdition, visible=False, key='MiscelaneousEdition', expand_x=True, expand_y=True),
         sg.Column(TypesEdition, visible=False, key='TypesEdition', expand_x=True, expand_y=True),
         sg.Column(ProductsEdition, visible=False, key='ProductsEdition', expand_x=True, expand_y=True)
         ]
    ]

    window = sg.Window('Budgeter', 
                    layout,
                    size=(Config.window_width, Config.window_height),
                    auto_size_buttons=False,
                    default_button_element_size=(Config.btn_width, Config.btn_height),
                    finalize=True
                    )
    window.SetIcon("E:\Projects\Python\DatabaseShenanigans\DatabaseShenanigans\Icon.ico")
    ChangeLayout(window, visibleelement)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        #Picked cell in table as per https://www.youtube.com/watch?v=ETHtvd-_FJg
        if isinstance(event, tuple):
            pass
            continue
        #Inserts
        if event in ('Configure'):
            #TODO ChangeLayout(window, 'Configure')
            continue
        if event in ('Miscelaneous'):
            ChangeLayout(window, 'MiscelaneousEdition')
            continue
        if event in ('Types'):
            ChangeLayout(window, 'TypesEdition')
            continue
        if event in ('Products'):
            ChangeLayout(window, 'ProductsEdition')
            continue
        if event in ('Expenditures'):
            ChangeLayout(window, 'ExpendituresEdition')
            continue
        if event in ('Bills'):
            ChangeLayout(window, 'BillsEdition')
            continue
        if event in ('Income'):
            ChangeLayout(window, 'IncomeEdition')
            continue
        if event in ('Income'):
            ChangeLayout(window, 'IncomeEdition')
            continue
        #Visualisations
        if event in ('Most common products'):
            ChangeLayout(window, 'Visualization')
            draw_figure(window['canvas'].TKCanvas, MostCommonProducts(Config.limit))
            continue
        if event in ('Income summary'):
            draw_figure(window['canvas'].TKCanvas, IncomeSummary())
            ChangeLayout(window, 'Visualization')
            continue
        if event in ('Monthly Bilance'):
            draw_figure(window['canvas'].TKCanvas, MonthlyBilance())
            ChangeLayout(window, 'Visualization')
            continue
        if event in ('TopTypeMonthly'):
            draw_figure(window['canvas'].TKCanvas, TopTypeMonthly())
            ChangeLayout(window, 'Visualization')
            continue
        if event in (products):    
            #product=values[0] #Alternative way - use if there will be more events
            draw_figure(window['canvas'].TKCanvas, GivenProduct(event.partition("(")[0]))
            ChangeLayout(window, 'Visualization')
            continue
        if event in (types):    
            #product=values[0] #Alternative way - use if there will be more events
            draw_figure(window['canvas'].TKCanvas, GivenType(event.partition("(")[0]))
            ChangeLayout(window, 'Visualization')
            continue
    window.close()

if __name__ == "__main__":
    main()