#------------------libraries used------------------
from shiny import* 
from shiny.express import *
from shinyswatch import theme
from itables.shiny import DT
from itables import show
import sqlite3
import pandas as pd


# Create SQLite database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()



def dataupload():
    return ui.markdown(
    """
    This section allow user to upload excel data file to SQLite database and displayed
     the recond from the uploaded dataset on DT """),ui.input_file("file", "Choose CSV File", accept=[".xlsx"], multiple=False),ui.input_checkbox("header", "Header", True), ui.input_action_button("Load_DB_Button",
    "Load Data",
    style = "bordered",
    width = "90%"),

ui.page_opts(title="PyshinyDataTable",fillable=True)
#-----------------------------Data-Upload-Section----------------
with ui.nav_panel("Upload-Data"):
    with ui.layout_sidebar():  
        with ui.sidebar(bg="#f8f8f8"):
            dataupload()
            ui.input_action_button("retrived","Show Record",)
            
        @render.ui
        @reactive.event(input.Load_DB_Button)
        def upload_excel_data():
            if input.file() is None:
                return "Please upload an Excel file"
            files: list[FileInfo] = input.file()
            for file in files:
                xls = pd.read_excel(file["datapath"], sheet_name=None)
                for sheet_name, df in xls.items():
                    if 'Hospital_No' in df.columns:
                        df = df.drop_duplicates(subset='Hospital_No', keep='first')
                        existing_hospitals = pd.read_sql(f"SELECT Hospital_No FROM {sheet_name}", conn)
                        df = df[~df['Hospital_No'].isin(existing_hospitals['Hospital_No'])]  # Filter out existing values
                    df.to_sql(sheet_name, conn, if_exists='append', index=False)
                else:
                    return "The records already exist on the Database Please check the record again or click on show record button to display the data" 
                     
            query = 'SELECT * FROM Outpatient'
            df = pd.read_sql_query(query, conn)

            return ui.HTML(DT(df,layout={"top": "searchBuilder"}, 
                            keys=True,classes="display nowrap compact", 
                                                buttons=["pageLength","copyHtml5", "csvHtml5", "excelHtml5",'print']))
        @render.ui
        @reactive.event(input.retrived)
        def showRecord():
            if input.retrived():
                query = 'SELECT * FROM Outpatient'
            df = pd.read_sql_query(query, conn)
            return ui.HTML(DT(df,layout={"top": "searchBuilder"}, 
                            keys=True,classes="display nowrap compact", 
                                                buttons=["pageLength","copyHtml5", "csvHtml5", "excelHtml5",'print']))   

