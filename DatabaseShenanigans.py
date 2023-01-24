# Required package to install
# pip install matplotlib first y'all via: python -m pip install -U matplotlib

#https://stackabuse.com/converting-strings-to-datetime-in-python/
#https://matplotlib.org/gallery/style_sheets/fivethirtyeight.html#sphx-glr-gallery-style-sheets-fivethirtyeight-py
#https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py
import sqlite3
import csv
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

themes=sg.theme_list()
import Config
finances_db=Config.Finances.fullpath
visibleelement=Config.startlayout
#------- Incantations end here -------------------------------------------------

#Class for cells
class Edition():
    def __init__(self,
                 table, 
                 ID, 
                 field, 
                 newvalue,
                 oldvalue): 
        self.table = table
        self.ID = ID
        self.field = field
        self.newvalue = newvalue
        self.oldvalue = oldvalue

    def __repr__(self): 
        return "Table % s modified. ID: % s field: % s oldvalue: % s newvalue: % s" % (self.table, 
                 self.ID, 
                 self.field, 
                 self.newvalue,
                 self.oldvalue)

edited_cells=[]     #Collection of editted cells

#Database stuff
def getfromdb(database, select):
    connection = sqlite3.connect(database)  #<TODO>Try this, repeat if connection fails
    cursor = connection.cursor()
    cursor.execute(select)
    rows=cursor.fetchall()
    connection.close()
    return rows
def SendToDB(table, todb):
    #TODO: Implement
    pass
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

#Config.databases['Finances'].schema=schema
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
    if len(edited_cells)>0:
        #TODO: Display popup window if user wants to commit changes to database
        pass
    window[visibleelement].update(visible=False)
    visibleelement=element
    window[visibleelement].update(visible=True)
def GetDataFromCSV(filename):
    content=csv.reader(open(filename,"r"))
    headers=next(content)
    data=list(content)
    return (headers, data)
#Modified edition from https://www.youtube.com/watch?v=ETHtvd-_FJg
def EditCell(window, key, row, col, edition):
    global textvariable, editcell

    def callback(event, row, col, text, key):
        global editcell
        widget = event.widget
        if key == 'Focus_Out':
            text = widget.get()     # Get typed text
        widget.destroy()
        widget.master.destroy()
        values = list(table.item(row, 'values'))
        values[col] = text
        edition.newvalue=text
        table.item(row, values=values)
        edited_cells.append(edition)
        editcell = False
    

    if editcell or row <= 0:
        return

    editcell = True
    table = window[key].Widget
    text = table.item(row, "values")[col]
    x, y, width, height = table.bbox(row, col)

    # Create a new container that acts as container for the editable text input widget
    # TODO: Fix edit box offset
    frame = sg.tk.Frame(window.TKroot)
    frame.place(x=x, y=y, anchor="nw", width=width, height=height)
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    entry = sg.tk.Entry(frame, textvariable=textvariable)
    entry.pack()
    entry.select_range(0, sg.tk.END)
    entry.icursor(sg.tk.END)
    entry.focus_force()
    # When you click outside of the selected widget, everything is returned back to normal
    # lambda e generates an empty function, which is turned into an event function 
    # which corresponds to the "FocusOut" (clicking outside of the cell) event
    entry.bind("<FocusOut>", lambda e, r=row, c=col, t=text, k='Focus_Out':callback(e, r, c, t, k))

def main():
    #layout preparation
    global editcell
    editcell=False
    products=Listfromtable("ProductSummary")
    types=Listfromtable("TypeSummary")
    sg.theme(Config.theme)
    menu = [['Visualizations', 
                ['Most common products', 
                 'Income summary',
                 'Monthly Bilance',
                 'TopTypeMonthly',
                 'Type'
                    ,[types],
                 'Product'
                    ,[products]]],
            ['Insert data',
                ['Expenditures',                #TODO
                 'Bills',                       #TODO
                 'Income',                      #TODO
                 'Types' ,                      #TODO
                 'Products',]],                 #TODO
                 #'Miscelaneous',]],            #TODO
            ['Options',                         #TODO
                ['Configure',                   #TODO
                #'Change Theme',                #TODO: Sadly not THAT easy
                #    [themes],
                'Version',
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
         sg.Column(TypesEdition, visible=False, key='TypesEdition', expand_x=True, expand_y=True),
         sg.Column(ProductsEdition, visible=False, key='ProductsEdition', expand_x=True, expand_y=True)
         #,sg.Column(MiscelaneousEdition, visible=False, key='MiscelaneousEdition', expand_x=True, expand_y=True)
         ]
    ]

    window = sg.Window('Budgeter', 
                    layout,
                    size=(Config.window_width, Config.window_height),
                    auto_size_buttons=False,
                    default_button_element_size=(Config.btn_width, Config.btn_height),
                    finalize=True
                    )
    window.SetIcon(Config.icon)
    ChangeLayout(window, visibleelement)

    #Specify events
    visualization_changes={
        'Configure'     : 'Configure',
        'Miscelaneous'  : 'MiscelaneousEdition',
        'Types'         : 'TypesEdition',
        'Products'      : 'ProductsEdition',
        'Expenditures'  : 'ExpendituresEdition',
        'Bills'         : 'BillsEdition',
        'Income'        : 'IncomeEdition'
    }
    popups={
        'TypesImport' : '',
        'ProductsImport' : '',
        'BillsImport' : '',
        'IncomeImport' : '',
        'ExpendituresImport' : '',
    }

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Exit', sg.WIN_CLOSED):
            break
        #Picked cell in table as per https://www.youtube.com/watch?v=ETHtvd-_FJg
        if isinstance(event, tuple):
            widget=event[0]
            table=widget.partition("_")[0]
            row=event[2][0]
            column=event[2][1]
            if isinstance(row, int) and row>-1:
                print(event[2])
                record=window[widget].widget.item(row+1, 'values')
                field=schema[table]['columns'][column]
                edition = Edition(widget, record[0], field, '', record[column])
                EditCell(window,widget,row+1,column, edition)
                print(edited_cells)
            elif isinstance(event[2][0], None):
                pass #add row
            continue
        #Inserts
        if event in (visualization_changes):
            ChangeLayout(window, visualization_changes[event])
            continue
        if event in (popups):
            table=event.partition("Import")[0]
            filename=sg.popup_get_file('Document to open')
            if filename is not (''):
                data=GetDataFromCSV(filename)
                todb=(Config.Finances.inserts[table], data)
                SendToDB(table, todb)
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
        if event in (themes):
            #change theme requires some serious work, leaving it as it is for now
            #https://github.com/PySimpleGUI/PySimpleGUI/issues/2437
            pass    
            continue
        #Defined in docummentation
        if event == 'Version':
            sg.popup_scrolled(sg.get_versions())
    window.close()

if __name__ == "__main__":
    main()