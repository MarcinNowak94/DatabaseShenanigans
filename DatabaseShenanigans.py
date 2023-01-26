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
app_name='Budgeter'
import Config
chosentheme=Config.theme

visibleelement=Config.startlayout
#------- Class definitions -----------------------------------------------------
class Database():
    def __init__(self, 
                 fullpath,
                 schema,
                 selects, 
                 inserts,
                 updates):
        self.fullpath = fullpath
        self.schema = schema
        self.selects = selects
        self.inserts = inserts
        self.updates = updates
class Chart():
    def __init__(self,
                 selects,
                 caption):
        self.selects = selects
        self.caption = caption
class CellEdition():
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

#------- Database interaction --------------------------------------------------
Finances=Database(
    fullpath=Config.fullpath,
    schema=[],
    selects=Config.selects,
    inserts=Config.inserts,
    updates={
        "UPDATE"                : "UPDATE table SET fieldsandvalues WHERE ID=record"
    }
)

def PrepareStatement(query, values):
    newquery=query.split("(")[0]+('(')
    #build query
    for col in values[0]:
        newquery+=(str(col)+", ")
    newquery=newquery.rstrip(", ") #delete trailing comma
    newquery+=") VALUES "
    for row in values:
        newquery+=('(')
        for col in row:
            newquery+=("'"+str(row[col])+"',")
        newquery=newquery.rstrip(",")+('),') #delete trailing comma
    newquery=newquery.rstrip(",")+(';') #delete trailing comma
    return newquery
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
def GetCollectionFromDB(collection):
    datasets=[]
    for select in collection.selects:
        data_from_db=GetFromDB(select.database[0],select.select[0])
        datasets.append((data_from_db, select.label))
    return datasets
def GetDBInfo(database):
    db={}
    for table in GetFromDB(database, Finances.selects['GetTables']):
        table=table[0] #Get only text
        select=Finances.selects['GetColumns'].replace(Config.placeholder, table)
        columns=GetFromDB(database, select)
        names=[]
        for values in columns:
            names.append(values[0])
        db[table]={"name": table, "columns": names}
    return db
Finances.schema=GetDBInfo(Finances.fullpath)

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
    values=GetFromDB(Finances.fullpath, Finances.selects[table])
    valuelist=[]
    
    for value in values:
        element = value[0]+"("+str(value[2])+")" if addvalues else value[0]
        valuelist.append(element)
    return valuelist


#------- Chart preparation -----------------------------------------------------
types=Listfromtable("TypeSummary")          #used only in menu so far
products= Listfromtable("ProductSummary")
topproductlist=[product.partition("(")[0] for product in products[0:Config.limit]] #TODO: Change so user can specify
top_type=GetFromDB(Finances.fullpath, Finances.selects['MostCommonProduct'])
if len(top_type):           #In case database is empty
    top_type=top_type[0][0] #Access value directly
else:
    top_type='none'
type_monthly= Finances.selects['GivenType'].replace(Config.placeholder, top_type)

def PrepareCharts():
    global topproductlist

    productselects=[]
    for product in topproductlist:
        productselects.append(
            ChartSelect(database=Finances.fullpath,
                select=Finances.selects['GivenProduct'].replace(Config.placeholder, product),
                label=product
                )
            )

    mostcommonproducts= Chart(
        selects=productselects,
        caption='Products'
    )
    
    global top_type
    global type_monthly

    toptypemonthly=Chart(
        selects={
            ChartSelect(
            database=Finances.fullpath,
            select=type_monthly,
            label=top_type
            )
        },
    caption=top_type+' products across time'
    )
    monthlyincome=Chart(
        selects={
            ChartSelect(
            database=Finances.fullpath,
            select=Finances.selects["MonthlyIncome"],
            label="Monthly income (label)"                          #TODO: (label) added for testing
            )
        },
        caption='Monthly income'
    )
    monthlybilance=Chart(
        selects={
            ChartSelect(
                database=Finances.fullpath,
                select=Finances.selects['MonthlyIncome'],
                label='Income'
            ),
            ChartSelect(
                database=Finances.fullpath,
                select=Finances.selects['MonthlyBills'],
                label='Bills'
            ),
            ChartSelect(
                database=Finances.fullpath,
                select=Finances.selects['MonthlyExpenditures'],
                label='Expenditures'
            ),
            ChartSelect(
                database=Finances.fullpath,
                select=Finances.selects['MonthlyBilance'],
                label='Bilance'
            )
            },
        caption='Bilance'
    )

    prepared_charts = {
        'Income summary' : monthlyincome,
        'Monthly Bilance' : monthlybilance,
        'Most common products': mostcommonproducts,
        'TopTypeMonthly' : toptypemonthly
    }
    return prepared_charts

def GivenProduct(product):
    chart=Chart(
        selects={
            ChartSelect(
            database=Finances.fullpath,
            select=Finances.selects['GivenProduct'].replace(Config.placeholder, product),
            label=product
            )
        },
        caption=product+' across time'
    )
    product_stats=GetCollectionFromDB(chart)
    return Prepare_plot(product_stats, chart.caption)
def GivenType(type):
    chart=Chart(
        selects={
            ChartSelect(
            database=Finances.fullpath,
            select=Finances.selects['GivenType'].replace(Config.placeholder, type),
            label=type
            )
        },
        caption=type+' across time'
    )
    product_stats=GetCollectionFromDB(chart)
    return Prepare_plot(product_stats, chart.caption)

#Layout and menu ---------------------------------------------------------------
def Visualize(chart):
    data= GetCollectionFromDB(chart)
    return Prepare_plot(data, chart.caption)
def TableToLayout(table):
    select=Finances.selects['AnyTable']
    select=select.replace(Config.placeholder, table['name'])
    vals=GetFromDB(Finances.fullpath, select)
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
    global Finances
    editor=[ [sg.Text(table+' Editor'), 
             sg.Button(key=table+'Import',
                    button_text='Import data',
                    tooltip='Import data from properly formatted CSV file. Example provided in resources directory.'),
             sg.Button(key=table+'AddRecord',
                        button_text='Add record',
                        tooltip='Add single record to '+table+' table')],
            [TableToLayout(Finances.schema[table])]]
    return editor
def TableInputWindow(name):
    global Finances
    layout=[[sg.Text(key='Info', text="Input desired data")]]
    #List slicing, bypass 1st element (usually ID)
    for column in Finances.schema[name]['columns'][1:]:
        #TODO: for *ID columns change to dropdown list 
        layout.append([sg.Text(column), sg.Input(key=column)])
    layout.append([sg.Ok(), sg.Cancel()])
    window=sg.Window(title="Add row to "+str(name), 
                     layout=layout,
                     icon=Config.icon,
                     modal=True,
                     element_justification='r')
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

def PrepareWindow(theme=chosentheme):
    #layout preparation
    global products
    global types
    global editcell
    editcell=False
    sg.theme(theme)
    menu = [['Visualizations', 
                ['Most common products', 
                 'Income summary',
                 'Monthly Bilance',
                 'TopTypeMonthly',
                 'Type'
                    ,[types],
                 'Product'
                    ,[products]]],
            ['Browse data',
                #TODO: Add views as uneditable
                ['Expenditures',                #TODO: Add Product dropdown
                 'Bills',
                 'Income',
                 'Types' ,
                 'Products',]],                 #TODO: Add TypeID dropdown
            ['Options',                         #TODO
                [#'Configure',                  #TODO: Stretch - config
                 'Change Theme',
                    [themes],
                'Version',
                'About...',
                'Manual']]                      #TODO: Wishful thinking - built in manual
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
    Splashscreen=[[sg.Column([[sg.Image(key='Logo', source=Config.logo)]], justification='center')],
                  [sg.Column([[sg.Text( key='App info',
                                        text='Project '+app_name+' v'+app_version+'. Poland, 2023.',
                                        justification='center',
                                        auto_size_text=True)]], justification='center')],
                  [sg.Column([[sg.Text( key='Authors',
                                        text='Authors: Nowak Marcin',
                                        justification='center',
                                        auto_size_text=True)]], justification='center')],
                  [sg.Column([[sg.Text( key='Versions',
                                        text='Used technologies:\n'+sg.get_versions(),
                                        justification='center',
                                        auto_size_text=True)]], justification='center')]
                ]
    UserManual=[[sg.Column([[sg.Text(key='Manual message',
                                     text='Section under construction. Please come back soon ...',
                                     auto_size_text=True)],
                            #TODO: figure out how text could wrap correctly itself
                            [sg.Text(key='Explaination_1',
                                     text=app_name+' is a simple application \
designed to aid users with managing their home budgets. After filling data user \
can generate graph /n to aid taking more',
                                     auto_size_text=True
                                     )],
                            [sg.Text(key='Explaination_2',
                                     text='educated choices by visualizing \
spending patterns, bilance and gruping expenditures by specific type or product.',
                                     auto_size_text=True,
                                     )]
                            ], justification='center')
                            ]]

    #TODO: Refresh after commiting data to table
    #Inspired by DEMO https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Column_Elem_Swap_Entire_Window.py
    layout=[
        [sg.Menu(key='Menu', menu_definition=menu)],
        [sg.Column(Splashscreen, key='About...', visible=False, expand_x=True, expand_y=True),
         sg.Column(UserManual, key='Manual', visible=False, expand_x=True, expand_y=True),
         sg.Column(Visualization, key='Visualization', visible=False,  expand_x=True, expand_y=True), 
         sg.Column(IncomeEdition, key='IncomeEdition', visible=False, expand_x=True, expand_y=True), 
         sg.Column(ExpendituresEdition, key='ExpendituresEdition', visible=False, expand_x=True, expand_y=True),
         sg.Column(BillsEdition, key='BillsEdition', visible=False, expand_x=True, expand_y=True),
         sg.Column(TypesEdition, key='TypesEdition', visible=False, expand_x=True, expand_y=True),
         sg.Column(ProductsEdition, key='ProductsEdition', visible=False, expand_x=True, expand_y=True)
         ]
    ]
    window = sg.Window(title=app_name+' v'+app_version, 
                    layout=layout,
                    size=(Config.window_width, Config.window_height),
                    auto_size_buttons=False,
                    default_button_element_size=(Config.btn_width, Config.btn_height),
                    finalize=True
                    )
    window.SetIcon(Config.icon)
    ChangeLayout(window, visibleelement)
    
    return window

def main():
    #close loading #TODO: Idea: turn into function and log how long startup took
    #------- Incantations end here -------------------------------------------------
    global chosentheme
    sg.theme(chosentheme)
    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, 
                        message='Welcome to '+app_name, 
                        title=app_name+' v'+app_version,
                        no_titlebar=False,
                        time_between_frames=100)


    window=PrepareWindow(theme=chosentheme)
    sg.popup_animated(None)
    #Specify events
    visualizations = PrepareCharts()
    visualization_changes={
        'Configure'     : 'Configure',
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
                field=Finances.schema[table]['columns'][column]
                edition = CellEdition(widget, record[0], field, '', record[column])
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
            filename=sg.popup_get_file(title='Import CSV', 
                                        message='Document to open', 
                                        icon=Config.icon)
            if filename not in (None, ''):                      #TODO: Validate propper path
                data=GetDataFromCSV(filename)
                todb=(Finances.inserts[table], data[1])
                SendToDB(Finances.fullpath, todb)
                #TODO: Refresh modified element data in layout
            continue
        if event in (addrecord):
            table=event.partition("AddRecord")[0]
            record=TableInputWindow(table)
            if record not in (None, '', []):        
                #TODO: Validate propper path
                todb=(Finances.inserts[table], [record])
                SendToDB(Finances.fullpath, todb)
                print(record)
                #An attempt was made
                window.close()
                window=PrepareWindow(chosentheme)
                #TODO: Refresh modified element data in layout
            continue
        #Visualisations
        if event in (visualizations):
            draw_figure(window['canvas'].TKCanvas, Visualize(visualizations[event]))
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
            #change themes on the fly requires some serious work, https://github.com/PySimpleGUI/PySimpleGUI/issues/2437
            #workaround
            chosentheme=event
            window.close()
            window=PrepareWindow(chosentheme)
            continue
        if event in ('About...', 'Manual'):
            #TODO: Either use as splash screen or create simple sg.popup()
            ChangeLayout(window, event)
            continue
        #Defined in docummentation
        if event == 'Version':
            sg.popup_scrolled(sg.get_versions())
    window.close()

if __name__ == "__main__":
    main()