window_width =  1920 #1024
window_height =  1080 #768
btn_width = 20
btn_height = 1
plot_width = window_width-btn_width-2
plot_height = window_height-10

limit=5 #top n products graphed
placeholder="placeholder"
startlayout="Visualization"

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

Finances=Database(
    fullpath="E:\Projects\Python\DatabaseShenanigans\DatabaseShenanigans\Resources\Test_DataSet\Budgeter_testbase.sqlite",
    schema=[],
    selects={
        "AnyTable"              : "SELECT * FROM ["+placeholder+"]",
        "Expenditures"          : "SELECT * FROM [Expenditures_Enriched];",
        "MonthlyExpenditures"   : "SELECT * FROM [MonthlyExpenditures];",
        "MonthlyIncome"         : "SELECT * FROM [MonthlyIncome];",
        "MonthlyBills"          : "SELECT * FROM [MonthlyBills];",
        "MonthlyProducts"       : "SELECT * FROM [Monthly_common_products];",
        "MostCommonProduct"     : "SELECT [Type] FROM [ProductTypeSummary] LIMIT 1;",
        "Comparison"            : "SELECT * FROM [Ledger_comparison];",
        "TypeSummary"           : "SELECT * FROM [ProductTypeSummary];",
        "GivenProduct"          : "SELECT SUBSTR([Datetime],1,7) AS [Month] \
                                          ,SUM([Amount])         AS [Amount] \
                                   FROM [Expenditures_Enriched] \
                                   WHERE [Product] LIKE '%"+placeholder+"%' \
                                   GROUP BY SUBSTR([Datetime],1,7);",
        "GivenType"             : "SELECT SUBSTR([Datetime],1,7) AS [Month] \
                                          ,SUM([Amount])         AS [Amount] \
                                   FROM [Expenditures_Enriched] \
                                   WHERE [Type] LIKE '%"+placeholder+"%' \
                                   GROUP BY SUBSTR([Datetime],1,7);",
        "ProductSummary"        : "SELECT * FROM [ProductSummary];",
        },
    
    inserts={
        "Income"                : "INSERT INTO [Income] (DateTime, Amount, Source, Type, Comment) VALUES ",
        "Bills"                 : "INSERT INTO [Bills]  (DateTime, Amount, Medium, Comment) VALUES ",
        "Expenditures"          : "INSERT INTO [Expenditures_transitory]  (DateTime, Amount, Product, Comment) VALUES ",
        "Products"              : "INSERT INTO [Products]  (Product, TypeID, Comment) VALUES ",
        "ProductTypes"          : "INSERT INTO [ProductTypes]  (DateTime, Amount, Medium, Comment) VALUES "        
    },

    updates={
        "UPDATE"                : "UPDATE table SET fieldsandvalues WHERE ID=record"
    }
    )
#Non-specific database selects
Common={
    "GetTables" : "SELECT [name] FROM sqlite_schema WHERE [type]='table';",
    "GetColumns" : "SELECT [name] FROM PRAGMA_TABLE_INFO('"+placeholder+"');"
}

databases=[Finances, Common];
