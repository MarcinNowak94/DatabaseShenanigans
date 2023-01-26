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
app_version='0.1'
import Config
finances_db=Config.Finances.fullpath
visibleelement=Config.startlayout
#------- Incantations end here -------------------------------------------------
sg.theme(Config.theme)
sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, 
                    message='Welcome to Budgeter', 
                    title='Budgeter v'+app_version,
                    no_titlebar=False,
                    time_between_frames=100)

#------- Class definitions -----------------------------------------------------
class Chart():
    def __init__(self,
                 selects,
                 caption):
        self.selects = selects
        self.caption = caption
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
class ChartSelect():
    def __init__(self,
                 database,
                 select,
                 label
                ):
        self.database=str(database),
        self.select=str(select),
        self.label=str(label)

edited_cells=[]     #Collection of editted cells

#------- Database stuff --------------------------------------------------------
def PrepareStatement(query, values):
    statement=query
    for row in values:
        statement+=('(')
        for col in row:
            statement+=("'"+str(col)+"',")
        statement=statement.rstrip(",") #delete trailing comma
        statement+=('),')
    statement=statement.rstrip(",") #delete trailing comma
    statement+=(';')
    return statement
def GetFromDB(database, select):
    #TODO: error handling
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(select)
    rows=cursor.fetchall()
    connection.close()
    return rows
def SendToDB(database, todb):
    #TODO: error handling
    #TODO: Fix encoding errors (Unicode)
    connection = sqlite3.connect(database)
    statement=PrepareStatement(todb[0], todb[1])
    connection.execute(statement)
    connection.commit()
    connection.close()

#TODO: Fix Chart(CohartSelect()) fields being lists instead of string
def GetCollectionFromDB_v2(collection):
    #select use [CONDITION] as placeholder for condition 
    datasets=[]
    for select in collection.selects:
        data_from_db=GetFromDB(select.database[0],select.select[0])
        datasets.append((data_from_db, select.label))
    return datasets
def GetCollectionFromDB(database, select_template, conditions):
    #select use [CONDITION] as placeholder for condition 
    datasets=[]
    select=''
    for condition in conditions:
        select=select_template.replace(Config.placeholder,condition)
        data_from_db=GetFromDB(database,select)
        datasets.append((data_from_db, condition))
    return datasets
def GetDBInfo(database):
    db={}
    for table in GetFromDB(database, Config.Common['GetTables']):
        table=table[0] #Get only text
        select=Config.Common['GetColumns'].replace(Config.placeholder, table)
        columns=GetFromDB(database, select)
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

def Listfromtable(table, addvalues=True):
    #Get list of common products from DB
    values=GetFromDB(finances_db, Config.Finances.selects[table])
    valuelist=[]
    
    for value in values:
        element = value[0]+"("+str(value[2])+")" if addvalues else value[0]
        valuelist.append(element)
    return valuelist

all_products= Listfromtable("ProductSummary")
product_list=[product.partition("(")[0] for product in all_products[0:Config.limit]] #TODO: Change so user can specify
productselects=[]
for product in product_list:
    productselects.append(
        ChartSelect(database=finances_db,
            select=Config.Finances.selects['GivenProduct'].replace(Config.placeholder, product),
            label=product
            )
        )
mostcommonproducts= Chart(
    selects=productselects,
    caption='Products'
)
top_type=GetFromDB(finances_db, Config.Finances.selects['MostCommonProduct'])
if len(top_type):           #In case database is empty
    top_type=top_type[0][0] #Access value directly
else:
    top_type='none'
type_monthly= Config.Finances.selects['GivenType'].replace(Config.placeholder, top_type)
toptypemonthly=Chart(
    selects={
        ChartSelect(
        database=finances_db,
        select=type_monthly,
        label=top_type
        )
    },
caption=top_type+' products across time'
)
monthlyincome=Chart(
    selects={
        ChartSelect(
        database=finances_db,
        select=Config.Finances.selects["MonthlyIncome"],
        label="Monthly income (label)"                          #TODO: (label) added for testing
        )
    },
    caption='Monthly income'
)
monthlybilance=Chart(
    selects={
        ChartSelect(
            database=finances_db,
            select=Config.Finances.selects['MonthlyIncome'],
            label='Income'
        ),
        ChartSelect(
            database=finances_db,
            select=Config.Finances.selects['MonthlyBills'],
            label='Bills'
        ),
        ChartSelect(
            database=finances_db,
            select=Config.Finances.selects['MonthlyExpenditures'],
            label='Expenditures'
        ),
        ChartSelect(
            database=finances_db,
            select=Config.Finances.selects['MonthlyBilance'],
            label='Bilance'
        )
        },
    caption='Bilance'
)

charts = {
    'Income summary' : monthlyincome,
    'Monthly Bilance' : monthlybilance,
    'Most common products': mostcommonproducts,
    'TopTypeMonthly' : toptypemonthly
}


def Visualize(chart):
    ChartSelect
    data= GetCollectionFromDB_v2(chart)
    return Prepare_plot(data, chart.caption)

def GivenProduct(Product):
    product_monthly=Config.Finances.selects['GivenProduct']
    product_stats=GetCollectionFromDB(finances_db, product_monthly, {Product})
    return Prepare_plot(product_stats, Product)
def GivenType(type):
    type_monthly=Config.Finances.selects['GivenType']
    type_stats=GetCollectionFromDB(finances_db, type_monthly, {type})
    return Prepare_plot(type_stats, type)

#Layout and menu ---------------------------------------------------------------
def TableToLayout(table, visible=True):
    select=Config.Finances.selects['AnyTable']
    select=select.replace(Config.placeholder, table['name'])
    vals=GetFromDB(finances_db, select)
    tableelement=sg.Table(key=table['name']+'_table',
                        values=vals,
                        headings=table['columns'],
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
                    tooltip='Import data from properly formatted CSV file. Example provided in resources directory.'),
             sg.Button(key=table+'AddRecord',
                        button_text='Add record',
                        tooltip='Add single record to '+table+' table')],
            [TableToLayout(schema[table])]]
    return editor
def TableInputWindow(name):
    global schema
    layout=[[sg.Text(key='Info', text="Input desired data")]]
    #List slicing, bypass 1st element (usually ID)
    for column in schema[name]['columns'][1:]:
        #TODO: for *ID columns change to dropdown list 
        layout.append([sg.Text(column), sg.Input(key=column)])
    layout.append([sg.Ok(), sg.Cancel()])
    window=sg.Window(title="Add row to "+str(name), layout=layout, modal=True, element_justification='r')
    record=[]
    while True:
        event, values = window.read()
        if event in (None, 'Cancel', sg.WIN_CLOSED):
            break
        if event in ('Ok'):
            record=values
            break
    window.close()
    return record
def ChangeLayout(window, element):
    global visibleelement
    if len(edited_cells)>0:
        #TODO: Display popup window if user wants to commit changes to database
        pass
    window[visibleelement].update(visible=False)
    visibleelement=element
    window[visibleelement].update(visible=True)
def GetDataFromCSV(filename):
    #Fixing encoding error, normally encoding is set to system default. Temporary
    #Bypass, ideally would deduce encoding using https://pypi.org/project/chardet/
    content=csv.reader(open(filename,"r",encoding="utf-8"))
    headers=next(content)
    data=list(content)
    return (headers, data)
#Modified edition from https://www.youtube.com/watch?v=ETHtvd-_FJg
#Solution is using TKInter - lower level library under PYSimpleGUI, 
#too advanced concept for the time being
#TODO: Fix offset due to table being nested inside column element and added buttons
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
                ['Expenditures',                #TODO: Add Product dropdown
                 'Bills',
                 'Income',
                 'Types' ,
                 'Products',]],                 #TODO: Add TypeID dropdown
            ['Options',                         #TODO
                ['Configure',                   #TODO: Stretch - config
                #'Change Theme',                #TODO: Sadly not THAT easy
                #    [themes],
                'Version',
                'About...']]                    #TODO: Optional
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
    
    #TODO: Refresh after commiting data to table
    #Inspired by DEMO https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Column_Elem_Swap_Entire_Window.py
    layout=[
        [sg.Menu(key='Menu', menu_definition=menu)],
        [sg.Column(Visualization, visible=False, key='Visualization', expand_x=True, expand_y=True), 
         sg.Column(IncomeEdition, visible=False, key='IncomeEdition', expand_x=True, expand_y=True), 
         sg.Column(ExpendituresEdition, visible=False, key='ExpendituresEdition', expand_x=True, expand_y=True),
         sg.Column(BillsEdition, visible=False, key='BillsEdition', expand_x=True, expand_y=True),
         sg.Column(TypesEdition, visible=False, key='TypesEdition', expand_x=True, expand_y=True),
         sg.Column(ProductsEdition, visible=False, key='ProductsEdition', expand_x=True, expand_y=True)
         ]
    ]

    #close loading #TODO: Idea: turn into function and log how long startup took
    sg.popup_animated(None)
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
        'ProductTypesImport' : '',
        'ProductsImport' : '',
        'BillsImport' : '',
        'IncomeImport' : '',
        'ExpendituresImport' : '',
    }
    addrecord={
        'ProductTypesAddRecord' : '',
        'ProductsAddRecord' : '',
        'BillsAddRecord' : '',
        'IncomeAddRecord' : '',
        'ExpendituresAddRecord' : '',
    }
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Exit', sg.WIN_CLOSED):
            break
        #Picked cell in table as per https://www.youtube.com/watch?v=ETHtvd-_FJg
        if isinstance(event, tuple) and event not in (None):
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
            if filename not in (None, ''):                      #TODO: Validate propper path
                data=GetDataFromCSV(filename)
                todb=(Config.Finances.inserts[table], data[1])
                SendToDB(Config.Finances.fullpath, todb)
                #TODO: Refresh modified element data in layout
            continue
        if event in (addrecord):
            table=event.partition("AddRecord")[0]
            record=TableInputWindow(table)
            if record not in (None, ''):                      #TODO: Validate propper path
                #todb=(Config.Finances.inserts[table], [record])
                #SendToDB(Config.Finances.fullpath, todb)
                print(record)
                #TODO: Refresh modified element data in layout
            continue
        #Visualisations
        if event in (charts):
            draw_figure(window['canvas'].TKCanvas, Visualize(charts[event]))
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
        if event in ('About...'):
            #TODO: Either use as splash screen or create simple sg.popup()
            pass
            continue
        #Defined in docummentation
        if event == 'Version':
            sg.popup_scrolled(sg.get_versions())
    window.close()

if __name__ == "__main__":
    main()