#!/usr/bin/python3

version  = 'gmocu-0.3, 2023-08-21'
database = 'gmocu.db'

# TODO:
# upload abi sequencing file to ICE

import PySimpleGUI as sg
import pysimplesqlmod as ss 
import os, sys
import ssl
import sqlite3
import pandas as pd
import numpy as np
import logging
import re
import icebreaker
from datetime import date
logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)               # <=== You can set the logging level here (NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL)

# Pyinstaller fix preventing reopening windows
from multiprocessing import freeze_support
freeze_support()

# get right path for pyinstaller
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)
logging.debug('CWD: ' + os.getcwd())

# set settings path
SETTINGS_PATH = '.'
sg.user_settings_filename(path=SETTINGS_PATH)

### autocomplete ###
input_width = 20
num_items_to_show = 5
orga_selection = []

# PySimpleGUI standard font size
os_font_size = 13
os_scale_factor = 1

# fix os-specific glitches
headings=[' ID ','  Name  ','                     Alias                       ','  Status  ','G '] # Table column widths can be set by the spacing of the headings!
features_headings = ['ID   ','   Annotation    ','                 Alias                 ','Risk ', 'Organism']
organisms_headings = ['ID   ','               Full name                  ','      Short name     ','RG    ']
spacer1 = '  '
spacer2 = '          '
spacer3 = '                   '
spacer4 = ' '
spacer5 = '                                '
spacer6 = '     '
spacer7 = '  '
spacer8 = '                              '
spacer9 = '                             '
spacer10 = '                             '
alias_length = 59

if sys.platform == "win32":
    headings=['ID',' Name ','            Alias            ','Status','G '] # Table column widths can be set by the spacing of the headings!
    features_headings = ['ID ','Annotation','        Alias        ','Risk', 'Organism']
    organisms_headings = ['ID','           Full name          ','Short name ','RG']
    spacer1 = ''
    spacer2 = '           '
    spacer3 = '                    '
    spacer4 = ''
    spacer5 = '                           '
    spacer6 = ' '
    spacer7 = ''
    spacer8 = '                              '
    spacer9 = '                             '
    spacer10 = '                             '
    alias_length = 59

elif sys.platform.startswith("linux"):  # could be "linux", "linux2", "linux3", ...
    headings=['ID','     Name     ','                            Alias                           ','     Status     ',' G '] # Table column widths can be set by the spacing of the headings!
    features_headings = ['ID ','     Annotation     ','                         Alias                       ','  Risk  ', '  Organism   ' ]
    organisms_headings = ['ID','                               Full name                             ','    Short name    ','  RG  ']
    spacer1 = ''
    spacer2 = '         '
    spacer3 = '                   '
    spacer4 = ''
    spacer5 = '                           '
    spacer6 = ' '
    spacer7 = ''
    spacer8 = '                              '
    spacer9 = '                             '
    spacer10 = '                             '
    alias_length = 57
    os_font_size = 13
    os_scale_factor = 1.6

# PySimpleGUI layout code
font_size = sg.user_settings_get_entry('-FONTSIZE-', os_font_size)
scale_factor = sg.user_settings_get_entry('-SCALE-', os_scale_factor)
sg.set_options(font=("Helvetica", font_size))
#sg.theme('DarkBlack')
sg.theme(sg.user_settings_get_entry('-THEME-', 'Reddit'))  # set the theme

img_base64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAABeAAAAXgH42Q/5AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAPtJREFUOI3tkjFKAwEQRd/fDZZCMCcQRFRCCi1SWdmksNDCC1jmAlmt0mRbsbDyAKKQQkstbAVtXG3EIwhpDRi/jcuuWTesvb+bYd5n+DOyTZl0+NzlEzteOymdKTNQL9kk0DUQYHccN28qGyhKFgl0h2l8t0YwaXvQepmeDQpw/3Ue6SoHA9RxeKkoqc800N5FyPv4DFgtrsUy0rn6t7XyDZZWjpE7BTjTFuOFox++aQY6eNoHTmfAmaxuehnZzic+V8kAPtLLiN7jdOJVNYJJu0agHdAQpeu5AeyWQEOkt6wMtwt/oChZR7r/Fbc3HDcf8q3CH/xV/wbwBe0pVw+ecPjyAAAAAElFTkSuQmCC'
img2_base64 = b'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAUCAYAAABSx2cSAAAACXBIWXMAAAJhAAACYQHBMFX6AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAOhJREFUOI3tz79OwlAUx/HvJTe1gW5iOqohcZHJuLv6Gs6uLvgADsbFGGZeQx+ADafqoEhiY4wabUyg/PFAexl0acCLneU3npzPOfkpaoEhT8RZM2dbHwAawNWKyqpjNeHnmFjSzEwDbPsurcOKFe83Hrlqx7MYIBokrJ/e/YpHk592KxKq4xuTwcZAX1JcrfA9Pf/Cd4ovvQmSGGa29jZLXB5sWCvs1jtcPw8pWLcWZIn/EQ5eR+xcPOTGGuhLYnjqjhVQzIXNSdUDUEf3ZRx5z/s5k2Y4oHretqJOJPNxLCm3b19/+jwFyitLV/vbA1oAAAAASUVORK5CYII='

##### Plasmid data #####
visible=[0,1,1,1,1] # Hide the primary key column in the table
record_columns=[
    ss.record('Plasmids.name',label='Plasmid name:',size=(35,10))+
    [sg.T("Clone:")]+
    ss.record('Plasmids.clone',no_label=True, size=(5,10))+
    ss.record('Plasmids.gb',no_label=True, visible=False, size=(0,10))+
    ss.record('Plasmids.date',no_label=True, readonly=True, size=(10,10)), # insvisible
    [sg.T(spacer8)]+
    ss.selector('cassettesSelector','Cassettes',size=(61,4)),
    ss.record('Cassettes.content',label='Cassette:',size=(46,10),)+
    [sg.Button('!', key=f'-info-', size=(1, 1)),]+
    ss.actions('cassettesActions','Cassettes', edit_protect=False, navigation=False, save=True, search=False),

    # autocomplete
    [sg.Text('Add Feature:' + spacer2)]+
    [sg.Input(size=(input_width, 1), enable_events=True, key='-AIN-')] +
    [sg.Text('Variant:')]+
    [sg.Input(size=(15, 1), key='-VARIANT-')]+
    [sg.Button(' ', image_data=img_base64, button_color = (sg.theme_background_color(), sg.theme_background_color()), key=f'-ADDFEATURE-')] +
    [sg.CB('Ignore Case', default=True, k='-IGNORE CASE-')],
    [sg.Text('                              ')] + [sg.pin(sg.Col([[sg.Listbox(values=[], size=(input_width, num_items_to_show), enable_events=True, key='-BOX-', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True)]], key='-BOX-CONTAINER-', pad=(0, 0), visible=False))],

    ss.record('Plasmids.alias',label='Alias: ',size=(alias_length,10))+[sg.Button('+', key=f'-ALIAS_IN-', size=(1, 1)),],
    ss.record('Plasmids.purpose',sg.MLine, (61, 3),label='Purpose: '),
    ss.record('Plasmids.summary',sg.MLine, (61, 3),label='Cloning summary: '),
    ss.record('Plasmids.backbone_vector',label= 'Orig. vector:', size=(29,10))+
    [sg.Text('Status:' + spacer1)] + ss.record('Plasmids.status',no_label=True, element=sg.Combo, quick_editor=False, size=(18,10))+
    ss.actions('plasmidActions','Plasmids', edit_protect=False,navigation=False,save=True, search=False, insert=False, delete=False),
    
   #[sg.Col([[sg.Text('GMOs:' + spacer3),]],vertical_alignment='t')] + ss.selector('gmoSelector','GMOs', size=(61,5)), #better for Windows
   [sg.Text('GMOs:' + spacer3),] + ss.selector('gmoSelector','GMOs', size=(61,5)), #better for macOS
   #[sg.T('                              '),] + ss.selector('gmoSelector', 'GMOs', element=sg.Table, headings=['ID', 'GMO_summary', 'Organism         ','Plasmid ID','Target RG', 'Date generated', 'Date destroyed'], visible_column_map=[0,0,1,0,1,1,1],num_rows=5),
    ss.record('Plasmids.organism_selector',element=sg.Combo, quick_editor=False, size=(24,10),)+
    [sg.T('Target RG:'+ spacer4),]+
    ss.record('Plasmids.target_RG',size=(3,10), no_label=True)+
    [sg.T('Approval: '),] + [sg.Input('-', size=(9,10), key='-APPROVAL-')],
    [sg.T(spacer5),] + [sg.T('Made / Destroyed:'),] + ss.record('Plasmids.generated',size=(10,10), no_label=True) + [sg.T(''),]+
    ss.record('Plasmids.destroyed',size=(10,10), no_label=True)+
    [sg.Button('Add', key=f'-ADDORGA-', size=(3, 1)),]+
    [sg.Button(':)', key=f'-ADDFAV-', size=(1, 1)),]+
    ss.actions('GMOActions','GMOs', edit_protect=False,navigation=False,save=False, search=False, insert=False)+
    [sg.Button('Destroy', key=f'-DESTROYORGA-', size=(6, 1)),],
]

selectors=[
    ss.actions('plasmidActions','Plasmids',search_size=(27, 1)) + [sg.Button('', image_data=img2_base64, button_color = (sg.theme_background_color(), sg.theme_background_color()), key=f'-DUPLICATE-')]+
    [sg.Button('ICE', key=f'-THISICE-', size=(3, 1)),],
    ss.selector('tableSelector', 'Plasmids', element=sg.Table, headings=headings, visible_column_map=visible,num_rows=12), #15 rows
]
'''
tablayout_plasmid = [
    [sg.Frame('Plasmids',selectors)],
    [sg.Col(record_columns,vertical_alignment='t')],
]
'''
# without frame
tablayout_plasmid = selectors + record_columns

sub_genebank = [ [sg.Text(spacer9),]+
    ss.record('Plasmids.gb_name', no_label=True, size=(42,10))+
    [sg.Text(""),]+
    [sg.Button('+', key=f'insGb', size=(1, 1)),]+
    [sg.Text(spacer6),]+
    [sg.Button('Download', key=f'-down_gb-', size=(8, 1)),]+
    ss.record('Plasmids.genebank',no_label=True, size=(1,10)),
]

tablayout_attach = [[sg.T(spacer10)]+

    ss.selector('attachmentSelector','Attachments', size=(39,4))+
    [sg.Text(spacer7),]+
    [sg.Button('+', key=f'insElement', size=(1, 1)),]+
    ss.actions('attachmentActions','Attachments', edit_protect=False,navigation=False,save=False,search=False,insert=False)+
    [sg.Button('Download', key=f'-down_att-', size=(8, 1)),],
]

tablayout_plasmid += [[sg.Frame('Genebank', sub_genebank)]]
tablayout_plasmid += [[sg.Frame('Attachments', tablayout_attach)]]

##### GMO #####
tablayout_GMO = [
    [sg.Text('Maintenance')],
    [sg.Button('Run', key=f'-CHECKFEATURES-'),] + [sg.Text('Check Nucleic acid feature glossary completeness')],
    [sg.Button('Run', key=f'-CHECKORGANISMS-'),] + [sg.Text('Check Organisms glossary completeness')], 
    [sg.Button('Run', key=f'-CHECKPLASMIDS-'),] + [sg.Text('Check for plasmid duplications and completeness')],
    [sg.Text('')],
    [sg.Text('jbei/ICE')], 
    [sg.Button('Run', key=f'-ICE-')] + [sg.Text('Upload/update all plasmid information and gb files to jbei/ICE')] + [sg.CB('Only new plasmids', default=True, k='-ONLYNEW-')],
    [sg.Text('')],
    [sg.Text('GMO')], 
    [sg.Button('Run', key=f'-PLASMIDLIST-'),] + [sg.Text('Generate plasmid list')],
    [sg.Button('Run', key=f'-FORMBLATT-'),] + [sg.Text('Generate Formblatt Z')],
    [sg.Text('')],
    [sg.Text('Data import')],
    [sg.Button('Run', key=f'-IMPORTGMOCU-'),] + [sg.Text('Import data from another gmocu database file')],
    #[sg.Output(size=(78, 20))],
]

##### Features #####
tablayout_Features = [
    ss.selector('featureSelector', 'Features', element=sg.Table, headings=features_headings , visible_column_map=[0,1,1,1,1],num_rows=40), #50
    ss.actions('featureActions','Features'),
    ss.record('Features.annotation',label='Annotation:', enable_events=True, size=(62,10)),
    ss.record('Features.alias',label='Alias:',size=(62,10)),
    ss.record('Features.risk',label='Risk:',size=(62,10)),
    #ss.record('Features.organism', element=sg.Combo, label='Organism:',size=(62,10)),
    [sg.Text("Organism:             ")] + [sg.Col([[sg.Combo(orga_selection, size=(26,10), enable_events=True, key='-FEATURECOMBO-')]], vertical_alignment='t')]+
    ss.record('Features.organism', no_label=True, size=(32,10)),
    [sg.Button('Export all to Excel', key=f'-ALLEXCEL-')] +
    [sg.Button('Export used to Excel', key=f'-USEDEXCEL-')],
    [sg.Button('Replace glossary with Excel file', key=f'-IMPEXCEL-')]+
    [sg.Button('Add entries from Excel which not yet exist', key=f'-ADDEXCEL-')],
    [sg.Button('Add entries from Google Sheet which not yet exist', key=f'-ADDGOOGLE-')]+
    [sg.Button('!', key=f'-FEATUREINFO-')],
    [sg.Text("Input file name: 'Downloads/templates/nucleic_acid_features.xlsx'")],
]

##### Organisms #####
tablayout_Organisms = [
    ss.selector('organismSelector', 'Organisms', element=sg.Table, headings=organisms_headings , visible_column_map=[0,1,1,1],num_rows=40), #50
    ss.actions('organismActions','Organisms'),
    #ss.record('Organisms.id',label='ID:',size=(62,10)),
    ss.record('Organisms.full_name',label='Full name:',size=(62,10)),
    ss.record('Organisms.short_name', label='Short name:',size=(62,10)),
    ss.record('Organisms.RG',label='RG:',size=(62,10)),
    [sg.Button('Export all to Excel', key=f'-ALLEXCELORGA-')] +
    [sg.Button('Export used to Excel', key=f'-USEDEXCELORGA-')],
    [sg.Button('Replace glossary with Excel file', key=f'-IMPEXCELORGA-')]+
    [sg.Button('Add entries from Excel which not yet exist', key=f'-ADDEXCELORGA-')],
    [sg.Button('Add entries from Google Sheet which not yet exist', key=f'-ADDGOOGLEORGA-')],
    [sg.Text("Input file name: 'Downloads/templates/organisms.xlsx'")],
]

##### Settings #####
tablayout_Settings = [
    ss.actions('settingsActions','Settings', edit_protect=True,navigation=False,save=True, search=False, insert=False, delete=False) + [sg.Button('Info', key=f'-SETTINGSINFO-'),],
    ss.record('Settings.name',label='Name:', size=(62,10)),
    ss.record('Settings.initials',label='Initials:', size=(62,10)),
    ss.record('Settings.email',label='Email:', size=(62,10)),
    ss.record('Settings.institution',label='GMO institute:', size=(62,10)),
    ss.record('Settings.ice',label='jbei/ICE API:', element=sg.Combo, size=(56,10)),
    ss.record('Settings.gdrive_glossary',label='Google Sheet ID:', size=(62,10)),
    [sg.Text("Style*:                   ")] + [sg.Col([[sg.Combo(['Reddit', 'DarkBlack', 'Black', 'BlueMono', 'BrownBlue', 'DarkBlue', 'LightBlue', 'LightGrey6'], default_value=sg.user_settings_get_entry('-THEME-', 'Reddit'), size=(60,10), enable_events=True, key='-SETSTYLE-')]], vertical_alignment='t')],
    ss.record('Settings.style',no_label=True, size=(29,10)),
    ss.record('Settings.scale',label='Scale factor*:', size=(62,10)),
    ss.record('Settings.font_size',label='Font size*:', size=(62,10)),
    ss.record('Settings.duplicate_gmos',label='Duplicate GMOs:', element=sg.CBox),
    ss.record('Settings.upload_completed',label='Upload completed:', element=sg.CBox),
    ss.record('Settings.upload_abi',label='Upload .ab1 files:', element=sg.CBox),
    [sg.Text('*Restart required')],
    [sg.Text('')],
    [sg.Text('Target organisms: ')] +
    [sg.Col([ss.selector('organismselectionSelector','OrganismSelection',size=(60,6)),
    [sg.Combo(orga_selection, size=(30,10), enable_events=True, key='-SETSELORGA-')]+
    [sg.Button('Add', key=f'-ADDSELORGA-')]+
    ss.actions('organismselectionActions','OrganismSelection', edit_protect=False, navigation=False, save=False, search=False, insert=False)], vertical_alignment='t')],
    [sg.Text('Fav. organisms:    ')] +
    [sg.Col([ss.selector('favouritesSelector','OrganismFavourites',size=(60,6)),
    [sg.Button('Copy', key=f'-COPYFAVORGA-')]+
    ss.actions('favouritesselectionActions','OrganismFavourites', edit_protect=False, navigation=False, save=False, search=False, insert=False)], vertical_alignment='t')],
    [sg.Text('                                  All listed organisms must also exist in Target organisms.')],
]

##### Tabs #####
layout = [[sg.TabGroup([[sg.Tab('Plasmid data', tablayout_plasmid, key='-pldata-'),
                         sg.Tab('GMO', tablayout_GMO),
                         sg.Tab('Nucleic acids', tablayout_Features),
                         sg.Tab('Organisms', tablayout_Organisms),
                         sg.Tab('Settings', tablayout_Settings),
                         ]], key='-tabs-', tab_location='top', selected_title_color='purple')],
                         ]
##### Window #####
win=sg.Window('GMOCU - GMO Documentation', layout, scaling=scale_factor, finalize=True)
win['Plasmids.gb_name'].update(disabled=True)
win['Plasmids.gb'].update(disabled=True)
win['Plasmids.genebank'].update(visible=False)
win['Settings.style'].update(visible=False)

sql_script ='gmocu.sql'
db=ss.Database(database, win,  sql_script=sql_script) #<=== Here is the magic!
# Note:  sql_script is only run if *.db does not exist!  This has the effect of creating a new blank
# database as defined by the sql_script file if the database does not yet exist, otherwise it will use the database!

#db['Plasmids'].set_order_clause('ORDER BY id ASC')
db['Cassettes'].set_order_clause('ORDER BY cassette_id ASC')
db['Plasmids'].set_search_order(['name','alias']) # the search box will search in both the name and example columns
db['Features'].set_search_order(['annotation','alias', 'organism']) # the search box will search in both the name and example columns
db.edit_protect()
selected_plasmid=db['Plasmids']['id']
db['Plasmids'].set_by_pk(selected_plasmid)

# disable extra elements
win['-DUPLICATE-'].update(disabled=True)
win['-THISICE-'].update(disabled=True)
win['-ALIAS_IN-'].update(disabled=True)
win['insGb'].update(disabled=True)
win['insElement'].update(disabled=True)
win['-down_att-'].update(disabled=True)
win['-down_gb-'].update(disabled=True)
win['-ADDORGA-'].update(disabled=True)
win['-DESTROYORGA-'].update(disabled=True)
win['-ADDFEATURE-'].update(disabled=True)
win['-FEATURECOMBO-'].update(disabled=True)
win['Features.organism'].update(disabled=True)
win['-APPROVAL-'].update(disabled=True)
win['Settings.name'].update(disabled=True)
win['Settings.initials'].update(disabled=True)
win['Settings.email'].update(disabled=True)
win['Settings.institution'].update(disabled=True)
win['Settings.ice'].update(disabled=True)
win['Settings.gdrive_glossary'].update(disabled=True)
win['Settings.style'].update(disabled=True)
win['-SETSTYLE-'].update(disabled=True)
win['Settings.scale'].update(disabled=True)
win['Settings.font_size'].update(disabled=True)
win['Settings.duplicate_gmos'].update(disabled=True)
win['Settings.upload_completed'].update(disabled=True)
win['Settings.upload_abi'].update(disabled=True)
win['-SETSELORGA-'].update(disabled=True)
win['-ADDSELORGA-'].update(disabled=True)
win['-COPYFAVORGA-'].update(disabled=True)
win['-ADDFAV-'].update(disabled=True)

# keyboard navigation
win.bind('<Down>', '-DOWNKEY-')
win.bind('<Up>', '-UPKEY-')
win.bind('<Return>', '-ENTERKEY-')
win.bind('<Escape>', '-ESCAPEKEY-')
win.bind('<Control-KeyPress-e>', '-CTRL-E-') # trigger event with key press combination

### read settings ###
def read_settings():
    ice = db['Settings']['ice']
    connection = sqlite3.connect(database)
    settings = pd.read_sql_query("SELECT * FROM Settings", connection)
    credits = pd.read_sql_query("SELECT * FROM IceCredentials WHERE id = {}".format(ice), connection)
    connection.close()

    user_name           = settings['name'][0]
    initials            = settings['initials'][0]
    email               = settings['email'][0]
    ice                 = settings['ice'][0]
    institution         = settings['institution'][0]
    duplicate_gmos      = settings['duplicate_gmos'][0]
    upload_completed    = settings['upload_completed'][0]
    upload_abi          = settings['upload_abi'][0]
    scale               = settings['scale'][0]
    font_size           = settings['font_size'][0]
    style               = settings['style'][0]

    ice_instance        = credits['ice_instance'][0]
    ice_token           = credits['ice_token'][0]
    ice_token_client    = credits['ice_token_client'][0]

    return [user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client]



l = read_settings()
user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client = l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13]

### GUI settings ###
if scale == '__':
    scale = os_scale_factor
if font_size == '__':
    font_size = os_font_size
    win['Settings.font_size'].update(font_size)
    win['Settings.scale'].update(scale)
    db['Settings'].save_record(display_message=False)

sg.user_settings_set_entry('-THEME-', style)
sg.user_settings_set_entry('-SCALE-', float(scale))
sg.user_settings_set_entry('-FONTSIZE-', int(font_size))

### autocomplete ###
def autocomp():
    connection = sqlite3.connect(database) 
    cursor = connection.cursor()
    choices = [job[0] for job in cursor.execute("SELECT annotation FROM Features")]
    cursor.close()
    connection.close()
    return sorted(choices)

### organism drop down ###
def select_orga():
    connection = sqlite3.connect(database) 
    cursor = connection.cursor()
    orga_selection = [job[0] for job in cursor.execute("SELECT short_name FROM Organisms")]
    cursor.close()
    connection.close()
    return sorted(orga_selection)

choices = autocomp()
orga_selection = select_orga()
win['-FEATURECOMBO-'].Update(values = orga_selection)
win['-SETSELORGA-'].Update(values = orga_selection)
#sg.popup(select_orga())

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def insertBLOB(plasmidId, file, filename):
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        sqlite_insert_blob_query = """ INSERT INTO Attachments
                                  (plasmid_id, file, filename) VALUES (?, ?, ?)"""

        attachment = convertToBinaryData(file)
        # Convert data into tuple format
        data_tuple = (plasmidId, attachment, filename)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if connection:
            connection.close()

def readBlobData(attId, attName):
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        path = "Downloads/"
        with open(path + attName, "wb") as output_file:
            cursor.execute("SELECT file FROM Attachments WHERE attach_id = ?", (attId,))
            ablob = cursor.fetchall()
            #sg.popup("ablob ", len(ablob))
            output_file.write(ablob[0][0])

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    except IsADirectoryError as iade:
        sg.popup("There is no attachment to download.")
    finally:
        if connection:
            connection.close()

def add_to_features(wb):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    annots = [annot[0] for annot in cursor.execute("SELECT annotation FROM Features")]
    wb['annotation'] = wb['annotation'].replace('-', '_', regex=True)
    wb['annotation'] = wb['annotation'].replace('\[', '(', regex=True)
    wb['annotation'] = wb['annotation'].replace(']', ')', regex=True)
    wb = wb[-wb["annotation"].isin(annots)] # remove rows from dataframe which are already in the table with the same annotation name
    wb  = wb.fillna(value='None')
    wb = wb.reset_index() # required for loop below indexing
    sg.popup('Adding: {}'.format(', '.join(wb['annotation'].tolist())))
    for idx in range(len(wb['annotation'])):
        cursor.execute("INSERT INTO Features (annotation, alias, risk, organism) VALUES (?, ?, ?, ?)", (wb['annotation'][idx], wb['alias'][idx], wb['risk'][idx], wb['organism'][idx]))
    connection.commit()
    connection.close()
    db['Features'].requery()

def add_to_organisms(wb):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    orgas = [annot[0] for annot in cursor.execute("SELECT short_name FROM Organisms")]
    wb = wb[-wb["short_name"].isin(orgas)] # remove rows from datafram which are already in the table with the same annotation name
    wb = wb.reset_index() # required for loop below indexing
    sg.popup('Adding: {}'.format(', '.join(wb['short_name'].tolist())))
    for idx in range(len(wb['short_name'])):
        #cursor.execute("INSERT INTO Organisms (short_name, full_name, RG) VALUES (?, ?, ?)", (wb['short_name'][idx], wb['full_name'][idx], format(float(wb['RG'][idx]),".0f")))
        cursor.execute("INSERT INTO Organisms (short_name, full_name, RG) VALUES (?, ?, ?)", (wb['short_name'][idx], wb['full_name'][idx], str(wb['RG'][idx])))
    connection.commit()
    connection.close()
    db['Organisms'].requery()

def generate_formblatt():

    try:

        fZ_data = pd.DataFrame({'Nr.':[],'Spender Bezeichnung':[],'Spender RG':[],'Empfänger Bezeichnung':[],'Empfänger RG':[],'Ausgangsvektor Bezeichnung':[],'Übertragene Nukleinsäure Bezeichnung':[],'Übertragene Nukleinsäure Gefährdungspotential':[],'GVO Bezeichnung':[],'GVO RG':[],'GVO Zulassung':[],'GVO erzeugt/erhalten am':[],'GVO entsorgt am':[],'Datum des Eintrags':[]})

        # get all GMOs as dataframe
        connection = sqlite3.connect(database)
        gmo_data = pd.read_sql_query("SELECT * FROM GMOs", connection)
        connection.close()

        # for each GMO, get the used cassettes of the plasmid
        for idx, gmo in gmo_data.iterrows():

            plasmid_id = gmo['plasmid_id']

            connection = sqlite3.connect(database)
            cassettes = pd.read_sql_query("SELECT content FROM Cassettes WHERE plasmid_id = {}".format(plasmid_id), connection)

            # split each cassette into the used features and combine
            used_features = cassettes['content'].tolist()
            # remove variants in []
            used_features = [re.sub('[\[].*?[\]]', '', feature) for feature in used_features]
            used_features = '-'.join(used_features).split('-')
        
            # get source organisms and risk for all used features
            feature_organisms = []
            feature_risk = []
            cursor = connection.cursor()
            for i in used_features:
                cursor.execute("SELECT organism FROM Features WHERE annotation = ?", (i,))
                element_organism = cursor.fetchone()
                feature_organisms.append(element_organism[0])
                cursor.execute("SELECT risk FROM Features WHERE annotation = ?", (i,))
                element_risk = cursor.fetchone()[0]
                if element_risk == None or element_risk == '':
                    element_risk = 'None'
                feature_risk.append(element_risk)
            
            # get RG for source organisms
            source_rg = []
            for i in feature_organisms:
                cursor.execute("SELECT RG FROM Organisms WHERE short_name = ?", (i,))
                element = cursor.fetchone()
                source_rg.append(element[0])

            # get RG for recipient organisms
            cursor.execute("SELECT RG FROM Organisms WHERE short_name = ?", (gmo['organism_name'],))
            recipient_rg = cursor.fetchone()

            # get organism full name
            cursor.execute("SELECT full_name FROM Organisms WHERE short_name = ?", (gmo['organism_name'],))
            recipient_orga_full_name = cursor.fetchone()[0]
            cursor.close()

            # get plasmid and original vector of plasmid
            plasmid_frame = pd.read_sql_query("SELECT name, backbone_vector FROM Plasmids WHERE id = {}".format(plasmid_id), connection)
            connection.close()
            plasmid_name = plasmid_frame['name'][0]
            original_plasmid = plasmid_frame['backbone_vector'][0]

            # pack data
            no              = str(idx + 1)
            donor           = '|'.join(feature_organisms)
            donor_rg        = '|'.join(source_rg)
            recipient       = recipient_orga_full_name
            recipient_rg    = recipient_rg[0]
            vector          = original_plasmid
            dna             = '|'.join(used_features)
            dna_risk        = '|'.join(feature_risk)
            gmo_name        = gmo['organism_name'] + '-' + plasmid_name
            gmo_rg          = gmo['target_RG']
            gmo_approval    = gmo['approval']
            date_generated  = gmo['date_generated']
            date_destroyed  = gmo['date_destroyed']
            #entry_date     = str(today.strftime("%Y-%m-%d")) # TODO:, fix
            entry_date      = gmo['date_generated']

            row = {'Nr.':no,'Spender Bezeichnung':donor,'Spender RG':donor_rg,'Empfänger Bezeichnung':recipient,'Empfänger RG':recipient_rg,'Ausgangsvektor Bezeichnung':vector,'Übertragene Nukleinsäure Bezeichnung':dna,'Übertragene Nukleinsäure Gefährdungspotential':dna_risk,'GVO Bezeichnung':gmo_name,'GVO RG':gmo_rg,'GVO Zulassung':gmo_approval,'GVO erzeugt/erhalten am':date_generated,'GVO entsorgt am':date_destroyed,'Datum des Eintrags':entry_date}
            
            #fZ_data = fZ_data.append(row, ignore_index=True) # Future warning
            fZ_data = pd.concat([fZ_data, pd.DataFrame.from_records([row])], ignore_index=True)
            
        return(fZ_data)

    except Exception as e:
        sg.popup(e)

def generate_plasmidlist():

    pL_data = pd.DataFrame({'Nr.':[],'Plasmid name':[],'Alias':[],'Clone':[],'Original vector':[],'Purpose':[],'Cloning summary':[],'Status':[],'Entry date':[]})

    # get all GMOs as dataframe
    connection = sqlite3.connect(database)
    plasmid_data = pd.read_sql_query("SELECT * FROM Plasmids", connection)
    status_values = pd.read_sql_query("SELECT * FROM SelectionValues ", connection)
    connection.close()

    # for each GMO, get the used cassettes of the plasmid
    for idx, plasmid in plasmid_data.iterrows():

        no              = idx+1
        name            = plasmid['name']
        alias           = plasmid['alias']
        clone           = plasmid['clone']
        original_vector = plasmid['backbone_vector']
        purpose         = plasmid['purpose']
        summary         = plasmid['summary']
        status          = status_values['value'][plasmid['status']-1]
        date            = plasmid['date']

        row = {'Nr.':no,'Plasmid name':name,'Alias':alias,'Clone':clone,'Original vector':original_vector,'Purpose':purpose,'Cloning summary':summary,'Status':status,'Entry date':date}
        
        pL_data = pd.concat([pL_data, pd.DataFrame.from_records([row])], ignore_index=True)
        
    return(pL_data)

def upload_ice(thisice):

    try:
        configuration = dict(
        root = ice_instance,
        token = ice_token,
        client = ice_token_client
        )
        ice = icebreaker.IceClient(configuration)

        # get all folders
        ice_folders = ice.get_collection_folders("PERSONAL")

        folderlist = []
        folder_ids = []
        newly_added_plasmids = []
        for i in ice_folders:
            folderlist.append(i['folderName'])
            folder_ids.append(i['id'])

        # create folder for user if not existing
        for a,b in zip(folderlist, folder_ids): # ice.get_folder_id not working?
            if a == initials:
                folder_id = b
        if initials not in folderlist:
            new_folder = ice.create_folder(initials)
            folder_id = new_folder['id']
            folderlist.append(initials)
            folder_ids.append(folder_id)

        # only get plasmids from user folder not from entire database, faster
        ice_plasmids = ice.get_folder_entries(folder_id)
        # or get all plasmids, this will decide if plasmid name duplicated in folders of users can exist. Changing the initials will cause duplications on the server as a new folder will be created.
        #ice_plasmids = ice.get_collection_entries("PERSONAL")
        ice_plasmid_names = [p['name'] for p in ice_plasmids]

        connection = sqlite3.connect(database)
        ### condition to overwrite local_plasmids here for THISICE button. Only upload/update the currently selected button.
        if thisice != '':
            local_plasmids = pd.read_sql_query("SELECT * FROM Plasmids WHERE name = (?)", connection, params=(thisice,))
        else:
            local_plasmids = pd.read_sql_query("SELECT * FROM Plasmids ", connection)
        status_values = pd.read_sql_query("SELECT * FROM SelectionValues ", connection)
        cassettes =  pd.read_sql_query("SELECT * FROM Cassettes ", connection)
        connection.close()

        layout = [[sg.Text('Uploading plasmids...', key="uploader")],
        [sg.ProgressBar(max_value=len(local_plasmids['id']), orientation='h', size=(20, 20), key='progress')]]

        upwin = sg.Window('ICE Upload', layout, finalize=True)
        # Get the element to make updating easier
        progress_bar = upwin['progress']
        
        for idx, plasmid in local_plasmids.iterrows():
            #upwin.Element('uploader').Update('Uploading ' + plasmid['name'])
            progress_bar.update_bar(idx)
            if upload_completed == 1 and plasmid['status'] != 1:
                pass
            if plasmid['name'] == 'p' + initials + '000' or '(Copy)' in plasmid['name']:
                sg.popup("Plasmid name '" + plasmid['name'] + "' is not allowed, no upload. Please change the name.")
                #sg.popup(plasmid['name'], plasmid['status'], ' not completed, no upload')

            else:
                if plasmid['name'] not in ice_plasmid_names: # create plasmid entry 
                    print('Creating plasmid ' + plasmid['name'] + ' in ICE...')
                    new = ice.create_plasmid(name=plasmid['name']) #element does somehow not contain the name odnly id but deposits with name, fix below
                    newly_added_plasmids.append(plasmid['name'])

                    new_part_id = new['id'] # fix to get name
                    fetched_again = ice.get_part_infos(new_part_id)
                    ice_plasmids.append(fetched_again)
                    ice_plasmid_names.append(plasmid['name'])
                    
                # update index with just created plasmids online, TODO: this takes too much time
                #ice_plasmids = ice.get_collection_entries("PERSONAL")
                #ice_plasmid_names = [p['name'] for p in ice_plasmids]


                addme = False
                if values['-ONLYNEW-'] == True and plasmid['name'] in newly_added_plasmids:
                    addme = True
                elif values['-ONLYNEW-'] == False:
                    addme = True
                if thisice != '': # overwrite checkbox setting in case thisice option is used for updating the currently selected plasmid.
                    addme = True

                if plasmid['name'] in ice_plasmid_names and addme == True:
                    print('Updating plasmid ' + plasmid['name'] + ' in ICE...')
                    upwin.Element('uploader').Update('Uploading ' + plasmid['name'])

                    for ice_p in ice_plasmids:
                        if plasmid['name'] == ice_p['name']:
                            d = {"type":"PLASMID",
                                "alias": plasmid['alias'],
                                "status": status_values['value'][plasmid['status']-1],
                                "shortDescription": plasmid['purpose'],
                                #"bioSafetyLevel": 1,
                                #"principalInvestigator": '',
                                #"principalInvestigatorEmail": '',
                                "creator": user_name,
                                "creatorEmail": email,
                                #"selectionMarkers": 'Amp',
                                "plasmidData": {
                                    "backbone": plasmid['backbone_vector'],
                                    "circular": "true"}}

                            ice.request("PUT","parts/"+str(ice_p['id']), data=d)

                            ice.set_part_custom_field(ice_p['id'], 'Clone', plasmid['clone'])
                            ice.set_part_custom_field(ice_p['id'], 'Cloning', plasmid['summary'])
                            ice.set_part_custom_field(ice_p['id'], 'Entry date', plasmid['date'])

                            # add all cassettes as custom fields
                            my_cassettes = cassettes[cassettes['plasmid_id']==plasmid['id']]['content']
                            for idx, cassette in enumerate(my_cassettes):
                                ice.set_part_custom_field(ice_p['id'], 'Cassette {}'.format(idx+1), cassette)

                            if plasmid['genebank'] != '':
                                try:
                                    ice.delete_part_record(ice_p['id'])
                                except:
                                    pass
                                ice.attach_record_to_part(ice_part_id=ice_p['id'], filename=plasmid['name'] + '.gb', record_text=plasmid['genebank'])
                            
                            ice.add_to_folder([ice_p['id']], folders_ids=[folder_id])

        upwin.close()
        sg.popup('Upload completed.')

    except Exception as e:
        sg.popup(e)

def add_oragnism(organism_index):
    selected_organism_index = organism_index
    choosen_target_RG = db['Plasmids']['target_RG']
    approval = values['-APPROVAL-']
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("SELECT organism_name FROM OrganismSelection WHERE orga_sel_id = ?", (selected_organism_index,))
    out = cursor.fetchone()
    value="'{0}'".format(out[0])
    db['GMOs'].insert_record(column='organism_name', value=value)
    if db['Plasmids']['destroyed'] == '':
        destroyed = 'tbd'
    else:
        destroyed = db['Plasmids']['destroyed']
    gmo_summary = 'RG ' + str(choosen_target_RG) + '   |   ' + 'Approval: ' + approval + '   |   ' + str(db['Plasmids']['generated']) + '   -   ' + str(destroyed) + '   |   ' + db['GMOs']['organism_name'].ljust(30)
    cursor.execute("UPDATE GMOs SET (target_RG, GMO_summary, date_generated, date_destroyed, approval) = (?, ?, ?, ?, ?) WHERE organism_id = (SELECT MAX(organism_id) FROM GMOs)", (choosen_target_RG, gmo_summary, db['Plasmids']['generated'], db['Plasmids']['destroyed'], approval))
    connection.commit()
    cursor.close()
    connection.close()

def import_data():

    file = sg.popup_get_file("Select file")
    connection = sqlite3.connect(database, timeout=60)
    cursor = connection.cursor()
    existing_plasmids = pd.read_sql_query("SELECT name, id FROM Plasmids", connection)
    existing_plasmid_names = existing_plasmids['name'].tolist()
    
    try:
        if file == '' or file == None:
            raise ValueError('No file selected.')
        cursor.execute("ATTACH DATABASE ? AS other", (file,))
        imp_plasmids = pd.read_sql_query("SELECT * FROM other.Plasmids", connection)
        imp_plasmids_names = imp_plasmids['name'].tolist()

        plasmids_to_import = np.setdiff1d(imp_plasmids_names, existing_plasmid_names) # yields the elements in `imp_plasmids_names` that are NOT in `existing_plasmid_names`
        plasmids_to_import_copy = plasmids_to_import

        selected_plasmids = []
        plasmids_to_import = plasmids_to_import.tolist()
        layout = [[sg.Text("The following plasmids do not yet exist and can be imported:")],      
                        [sg.Listbox(values=plasmids_to_import, size=(30,6), enable_events=True, key="-LIST-"), sg.Button("Add", enable_events=True, key="-BUTTON-"), sg.Button("Remove", enable_events=True, key="-BUTTON2-"), sg.Listbox(values=selected_plasmids, size=(30,6), key="-LIST2-")],
                        [sg.Button("Import selected", enable_events=True, key="-BUTTON3-")]+ [sg.Button("Import all", enable_events=True, key="-BUTTON4-")], 
                        ]  

        selwin = sg.Window("Import selection", layout=layout)

        while True:
            event, values = selwin.read()
            try:
                if event == sg.WIN_CLOSED:
                    selected_plasmids = []
                    break
                
                if event == "-BUTTON-":
                    INDEX = int(''.join(map(str, selwin["-LIST-"].get_indexes())))
                    selected_plasmids.append(plasmids_to_import.pop(INDEX))
                    selwin["-LIST2-"].update(selected_plasmids)
                    selwin["-LIST-"].update(plasmids_to_import)

                if event == "-BUTTON2-":
                    INDEX = int(''.join(map(str, selwin["-LIST2-"].get_indexes())))
                    plasmids_to_import.append(selected_plasmids.pop(INDEX))
                    selwin["-LIST2-"].update(selected_plasmids)
                    selwin["-LIST-"].update(plasmids_to_import)

                if event == "-BUTTON3-":
                    break

                if event == "-BUTTON4-":
                    selected_plasmids = plasmids_to_import_copy
                    break
            except:
                pass

        selwin.close()

    except Exception as e:
        sg.popup(e)

    try:
        if len(selected_plasmids) > 0:
            name = 'gmocu_backup_{}.db'.format(str(date.today().strftime("%Y-%m-%d")))
            backup = sg.popup_yes_no('Shall we make a backup of the current database in the Download folder as {}'.format(name))
            if backup == 'Yes':
                path = 'Downloads/' + name

                def progress(status, remaining, total):
                    print(f'Copied {total-remaining} of {total} pages...')

                src = sqlite3.connect(database)
                dst = sqlite3.connect(path)
                with dst:
                    src.backup(dst, pages=1, progress=progress)
                dst.close()
                src.close()


        added_cassette_ids = []
        imported_plasmid_ids = []

        for idx, plasmid in imp_plasmids.iterrows():
            if plasmid['name'] not in existing_plasmid_names and plasmid['name'] in selected_plasmids:
                print('Importing plasmid ', plasmid['name'])
                imported_plasmid_ids.append(plasmid['id'])
                # insert new plasmid and copy values if plasmid name does not yet exist
                cursor.execute("INSERT INTO Plasmids (name, alias, status, purpose, gb, summary, genebank, gb_name, FKattachment, clone, backbone_vector, marker, organism_selector, target_RG, generated, destroyed, date) SELECT name, alias, status, purpose, gb, summary, genebank, gb_name, FKattachment, clone, backbone_vector, marker, organism_selector, target_RG, generated, destroyed, date FROM other.Plasmids WHERE other.Plasmids.id = ?", (plasmid['id'],))
                cursor.execute("SELECT MAX(id) FROM Plasmids")
                max_plasmid_id = cursor.fetchone()[0]
                # insert new cassette and copy content for current plasmid , leave plasmid_id empty
                cursor.execute("INSERT INTO Cassettes (content) SELECT content FROM other.Cassettes WHERE other.Cassettes.plasmid_id = ?", (plasmid['id'],))
                # get all new cassette ids for entries which still lack the plasmid_id
                cursor.execute("SELECT cassette_id FROM Cassettes WHERE plasmid_id IS NULL")
                cassette_ids = cursor.fetchall()
                for i in cassette_ids:
                    # update plasmid_id in Cassettes with new plasmid_id (max, last added)
                    cursor.execute("UPDATE Cassettes SET plasmid_id = ? WHERE cassette_id = ?", (max_plasmid_id, i[0]))
                    added_cassette_ids.append(i[0])

                # insert new GMO and copy content for current plasmid, leave plasmid_id empty
                cursor.execute("INSERT INTO GMOs (GMO_summary, organism_name, approval, target_RG, date_generated, date_destroyed, entry_date) SELECT GMO_summary, organism_name, approval, target_RG, date_generated, date_destroyed, entry_date FROM other.GMOs WHERE other.GMOs.plasmid_id = ?", (plasmid['id'],))
                cursor.execute("SELECT organism_id FROM GMOs WHERE plasmid_id IS NULL")
                organism_ids = cursor.fetchall()
                for i in organism_ids:
                    cursor.execute("UPDATE GMOs SET plasmid_id = ? WHERE organism_id = ?", (max_plasmid_id, i[0]))
                
                # insert new attachment and copy content for current plasmid, leave plasmid_id empty
                cursor.execute("INSERT INTO Attachments (file, Filename) SELECT file, Filename FROM other.Attachments WHERE other.Attachments.plasmid_id = ?", (plasmid['id'],))
                cursor.execute("SELECT attach_id FROM Attachments WHERE plasmid_id IS NULL")
                attach_ids = cursor.fetchall()
                for i in attach_ids:
                    cursor.execute("UPDATE Attachments SET plasmid_id = ? WHERE attach_id = ?", (max_plasmid_id, i[0]))

        connection.commit()

        unique_imported_features = set()
        cassettes = pd.read_sql_query("SELECT * FROM Cassettes", connection)
        for idx, added_cassette in cassettes.iterrows():
            if added_cassette['cassette_id'] in added_cassette_ids:
                added_cassette_elements = added_cassette['content']
                added_cassette_elements = re.sub('[\[].*?[\]]', '', added_cassette_elements) 
                added_cassette_elements = added_cassette_elements.split('-')
                for i in added_cassette_elements:
                    unique_imported_features.add(i)

        unique_imported_features = list(unique_imported_features)
        features = pd.read_sql_query("SELECT annotation FROM Features", connection)
        features_list = features['annotation'].tolist()
        missing_features = np.setdiff1d(unique_imported_features, features_list) # yields the elements in `unique_imported_features` that are NOT in `features_list`
        if len(missing_features) > 0:
            sg.popup('The following Nucleic acid features are missing and will be imported:\n', ', '.join(missing_features))
            for i in missing_features:
                print('Adding nucleic acid feature ', i)
                cursor.execute("INSERT INTO Features (annotation, alias, risk, organism) SELECT annotation, alias, risk, organism FROM other.Features WHERE other.Features.annotation = ?", (i,))
            connection.commit()
        if len(missing_features) > 1:
            missing_organisms_from_features = pd.read_sql_query('SELECT organism FROM Features WHERE annotation IN {}'.format(str(tuple(missing_features))), connection)
        else:
            missing_organisms_from_features = pd.read_sql_query('SELECT organism FROM Features WHERE annotation = {}'.format(str(missing_features[0])), connection)
        if len(imported_plasmid_ids) > 1:
            missing_organisms_from_gmos = pd.read_sql_query('SELECT organism_name FROM other.GMOs WHERE plasmid_id IN {}'.format(str(tuple(imported_plasmid_ids))), connection)
        else:
            missing_organisms_from_gmos = pd.read_sql_query('SELECT organism_name FROM other.GMOs WHERE plasmid_id = {}'.format(str(imported_plasmid_ids[0])), connection)
        missing_organisms_from_gmos = missing_organisms_from_gmos.rename(columns={'organism_name': 'organism'})
        missing_organisms = pd.concat([missing_organisms_from_features['organism'], missing_organisms_from_gmos['organism']], ignore_index=True)
        unique_missing_organisms = set()
        for idx, orga in missing_organisms.items():
            unique_missing_organisms.add(orga)

        unique_missing_organisms = list(unique_missing_organisms)
        if len(unique_missing_organisms) > 0:
            sg.popup('The following Organisms are used by the imported nucleic acid features and generated GMOs but are missing and will be added:\n', ', '.join(unique_missing_organisms))
            for i in unique_missing_organisms:
                print('Adding organism ', i)
                cursor.execute("INSERT INTO Organisms (full_name, short_name, RG) SELECT full_name, short_name, RG FROM other.Organisms WHERE other.Organisms.short_name = ?", (i,))
            connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:
        pass

def check_plasmids():
    try:
        connection = sqlite3.connect(database)
        plasmids = pd.read_sql_query("SELECT name, id FROM Plasmids ", connection)
        plasmid_names = list(plasmids['name'])
        plasmid_ids = list(plasmids['id'])
        seen = set()
        dupes = [x for x in plasmid_names if x in seen or seen.add(x)]

        plasmids_wo_backbone =  pd.read_sql_query("SELECT name FROM Plasmids WHERE backbone_vector = '' ", connection)
        plasmids_wo_backbone = list(plasmids_wo_backbone['name'])

        plasmid_wo_cassettes = []
        cassettes_pids = pd.read_sql_query("SELECT plasmid_id FROM Cassettes", connection)
        cassettes_pids = list(cassettes_pids['plasmid_id'])
        for pid in plasmid_ids:
            if pid not in cassettes_pids:
                plasmid_wo_cassettes.append(plasmids[plasmids['id']==pid]['name'].values[0])

        plasmid_wo_gmos = []
        gmo_pids = pd.read_sql_query("SELECT plasmid_id FROM GMOs", connection)
        connection.close()
        gmo_pids = list(gmo_pids['plasmid_id'])
        for pid in plasmid_ids:
            if pid not in gmo_pids:
                plasmid_wo_gmos.append(plasmids[plasmids['id']==pid]['name'].values[0])
        
        return [dupes, plasmids_wo_backbone, plasmid_wo_cassettes, plasmid_wo_gmos]

    except Exception as e:
        sg.popup(e)

def check_features():
    try:
        connection = sqlite3.connect(database)
        glossay_features = pd.read_sql_query("SELECT annotation FROM Features ", connection)
        glossay_features = list(glossay_features['annotation'])
        # check for duplicates in glossary_features
        seen = set()
        dupes = [x for x in glossay_features if x in seen or seen.add(x)]
        used_features = pd.read_sql_query("SELECT content FROM Cassettes ", connection)
        used_features = list(used_features['content'])
        # remove variants in []
        used_features = [re.sub('[\[].*?[\]]', '', feature) for feature in used_features] ## TODO: fix also in generate_formabaltt
        used_features = '-'.join(used_features).split('-')
        connection.close()
        comparison = np.setdiff1d(used_features, glossay_features) # yields the elements in `used_features` that are NOT in `glossay_features`
        redundant = np.setdiff1d(glossay_features, used_features)
        nonmissing = ''
        if len(comparison) == 0:
            nonmissing = True
        else:
            sg.popup('The following features are used as cassettes but missing in the Nucleic acids feature glossary:\n', ",".join(comparison), '\n Please add them!')

        return [nonmissing, redundant, dupes]
    except Exception as e:
        sg.popup(e)

def check_organisms():
    try:
        connection = sqlite3.connect(database)
        feature_organisms = pd.read_sql_query("SELECT annotation, organism FROM Features ", connection)
        gmo_organisms = pd.read_sql_query("SELECT organism_name FROM GMOs ", connection)
        feature_organisms_list = list(feature_organisms['organism'])
        gmo_organisms_list = list(gmo_organisms['organism_name'])
        used_organisms_list = feature_organisms_list + gmo_organisms_list
        organissm_glossary = pd.read_sql_query("SELECT short_name FROM Organisms ", connection)
        organissm_glossary_list = list(organissm_glossary['short_name'])
        connection.close()
        # check for duplicates in organissm_glossary_list
        seen = set()
        dupes = [x for x in organissm_glossary_list if x in seen or seen.add(x)]
        missing_feature_organisms = np.setdiff1d(used_organisms_list, organissm_glossary_list)
        redundant = np.setdiff1d(organissm_glossary_list, used_organisms_list)
        nonmissing = ''
        if len(missing_feature_organisms) == 0:
            nonmissing = True
        else:
            sg.popup('The following organisms are associated with used Nucleic acids features but are not in the Organism glossary:\n', ",".join(missing_feature_organisms), '\n Please add them!')
        return [nonmissing, redundant, dupes]
    except Exception as e:
        sg.popup(e)

### autocomplete ###
list_element:sg.Listbox = win.Element('-BOX-')           # store listbox element for easier access and to get to docstrings
prediction_list, input_text, sel_item = [], "", 0

# call initials on first start, changing initals later is not allowed because it might create a mess when updating plasmids on ice as a new folder would be created
initials_value = db['Settings']['initials']
if initials_value == '__':
    initials_set = sg.popup_get_text('Please enter your initials. This name will be used as folder name when uploading plasmids to ice.\nPlease note that you cannot change the name anymore at a later time.')
    win['Settings.initials'].update(initials_set)
    db['Settings'].save_record(display_message=False)


# WHILE
#-------------------------------------------------------
while True:
    event, values = win.read()
    #print('event:', event)
    #print('values:', values)

### Fix display ###
    if event == 'cassettesActions.table_insert':
        db['Plasmids'].save_record(display_message=False)
        selected_plasmid=db['Plasmids']['id']
        db['Plasmids'].set_by_pk(selected_plasmid)
    elif event == 'featureActions.db_save':
        db['Features'].save_record(display_message=False)
        corrected_value = db['Features']['annotation']
        corrected_value = corrected_value.replace('-', '_')
        corrected_value = corrected_value.replace('[', '(')
        corrected_value = corrected_value.replace(']', ')')
        win['Features.annotation'].update(corrected_value)
        choices = autocomp()
    elif event == 'settingsActions.db_save':
        db['Settings'].save_record(display_message=False)
        l = read_settings()
        user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client = l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13]
        sg.user_settings_set_entry('-THEME-', (values['Settings.style']))
        sg.user_settings_set_entry('-SCALE-', (values['Settings.scale']))
        sg.user_settings_set_entry('-FONTSIZE-', (values['Settings.font_size']))
        win['Settings.style'].update(disabled=True) # not a perfect solution
        win['Settings.style'].update(value=values['-SETSTYLE-'])
    elif event == 'insElement':
        db['Plasmids'].save_record(display_message=False)
    elif event == 'plasmidActions.edit_protect':
        # enable extra elements
        win['-DUPLICATE-'].update(disabled=False)
        win['-THISICE-'].update(disabled=False)
        win['-ADDFEATURE-'].update(disabled=False)
        win['-ALIAS_IN-'].update(disabled=False)
        win['insGb'].update(disabled=False)
        win['insElement'].update(disabled=False)
        win['-down_att-'].update(disabled=False)
        win['-down_gb-'].update(disabled=False)
        win['-ADDORGA-'].update(disabled=False)
        win['-DESTROYORGA-'].update(disabled=False)
        win['-APPROVAL-'].update(disabled=False)
        win['-ADDFAV-'].update(disabled=False)
    elif event == 'featureActions.edit_protect':
        win['-FEATURECOMBO-'].update(disabled=False)

        #win['Features.organism'].update(disabled=True) #always disabled, not working?
    elif event == 'settingsActions.edit_protect':
        win['Settings.name'].update(disabled=False)
        win['Settings.initials'].update(disabled=True)
        win['Settings.email'].update(disabled=False)
        win['Settings.institution'].update(disabled=False)
        win['Settings.ice'].update(disabled=False)
        win['Settings.gdrive_glossary'].update(disabled=False)
        win['Settings.style'].update(disabled=False)
        win['-SETSTYLE-'].update(disabled=False)
        win['Settings.scale'].update(disabled=True) # disable here if needed
        win['Settings.font_size'].update(disabled=True) # disable here if needed
        win['Settings.duplicate_gmos'].update(disabled=False)
        win['Settings.upload_completed'].update(disabled=False)
        win['Settings.upload_abi'].update(disabled=True) # disabled for now
        win['-SETSELORGA-'].update(disabled=False)
        win['-ADDSELORGA-'].update(disabled=False)
        win['-COPYFAVORGA-'].update(disabled=False)

### Let PySimpleSQL process its own events! Simple! ###
    if db.process_events(event, values):
        logger.info(f'PySimpleDB event handler handled the event {event}!')

    if event == 'plasmidActions.table_insert':
        selected_plasmid=db['Plasmids']['id']
        newname = 'p' + initials + '000'
        newname_input = sg.popup_get_text('Enter the name for the new plasmid', default_text=newname)
        win['Plasmids.name'].update(newname_input)
        db['Plasmids'].save_record(display_message=False)
        db['Plasmids'].set_by_pk(selected_plasmid)

    elif event == 'featureActions.table_delete':
        choices = autocomp()

    elif event == 'organismActions.table_delete':
        orga_selection = select_orga()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)

    elif event == 'organismActions.db_save':
        orga_selection = select_orga()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)

### Duplicate plasmid ###
    elif event == '-DUPLICATE-':
        duplicate_plasmid = sg.popup_yes_no('Do you wish to duplicate the plasmid entry?')
        if duplicate_plasmid == 'Yes':
            l = read_settings()
            user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client = l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13]
            today = date.today()
            selected_plasmid = db['Plasmids']['id']
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Plasmids (name, alias, purpose, summary, clone, backbone_vector) SELECT name, alias, purpose, summary, clone, backbone_vector FROM Plasmids WHERE Plasmids.id = ?", (selected_plasmid,))
            cursor.execute("SELECT MAX(id) FROM Plasmids")
            out = cursor.fetchone()[0]
            connection.commit()
            # duplicate cassettes
            cursor.execute("SELECT content, plasmid_id FROM Cassettes WHERE plasmid_id = ?", (selected_plasmid,))
            cas = cursor.fetchall()
            for i in cas:
                db['Cassettes'].insert_record(column='plasmid_id', value=out)
                cursor.execute("UPDATE Cassettes SET content = ? WHERE cassette_id = (SELECT MAX(cassette_id) FROM Cassettes)", (i[0],))
                connection.commit()
            # duplicate GMOs if selected in settings but with current date
            if duplicate_gmos == 1:
                cursor.execute("SELECT organism_name, plasmid_id, target_RG, approval FROM GMOs WHERE plasmid_id = ?", (selected_plasmid,))
                gmos = cursor.fetchall()
                for i in gmos:
                    db['GMOs'].insert_record(column='plasmid_id', value=out)
                    gmo_summary = 'RG ' + str(i[2]) + '   |   ' + 'Approval: ' + i[3] + '   |   ' + str(today.strftime("%Y-%m-%d")) + '   -   ' + 'tbd' + '   |   ' + i[0].ljust(30)
                    cursor.execute("UPDATE GMOs SET (organism_name, target_RG, GMO_summary, approval) = (?, ?, ?, ?) WHERE organism_id = (SELECT MAX(organism_id) FROM GMOs)", (i[0], i[2], gmo_summary, i[3])) 
                    connection.commit()
            cursor.close()
            connection.close()
            db['Plasmids'].save_record(display_message=False)
            db['Plasmids'].set_by_pk(out)
            win['Plasmids.name'].update(db['Plasmids']['name'] + ' (Copy)')
            db['Plasmids'].save_record(display_message=False)
            db['Plasmids'].set_by_pk(out)
        
### GMOs ###
    elif event == '-THISICE-':
        thisice = db['Plasmids']['name']
        upload = sg.popup_yes_no('Updating plasmid {} on ICE. Proceed?'.format(thisice))
        if upload == 'Yes':
            upload_ice(thisice)
    elif event == '-ADDORGA-':
        try:
            db['Plasmids'].save_record(display_message=False)
            selected_plasmid = db['Plasmids']['id']
            organism_index = db['Plasmids']['organism_selector']
            add_oragnism(organism_index)

        except TypeError:
            sg.popup("Choose an organism.")
        finally:
            win["Plasmids.organism_selector"]('')
            db['Plasmids'].save_record(display_message=False)
            db['Plasmids'].set_by_pk(selected_plasmid)

    elif event == '-ADDFAV-': 
        addfav = sg.popup_yes_no('Adding all favourite organisms as GMOs. Proceed?')
        if addfav == 'Yes':
            try:
                db['Plasmids'].save_record(display_message=False)
                selected_plasmid = db['Plasmids']['id']
                connection = sqlite3.connect(database)
                cursor = connection.cursor()
                favs = pd.read_sql_query("SELECT * FROM OrganismFavourites", connection)
                target_orgas = pd.read_sql_query("SELECT * FROM OrganismSelection", connection)
                comparison = np.setdiff1d(list(favs['organism_fav_name']), list(target_orgas['organism_name'])) # yields the elements in `favs` that are NOT in `target_orgas`
                if len(comparison) > 0:
                    sg.popup('Settings: Not all elements in Favourite organisms are present in Target organisms. Please fix!')
                else:
                    for idx, fav in favs.iterrows():
                        cursor.execute("SELECT orga_sel_id FROM OrganismSelection WHERE organism_name = ?", (fav['organism_fav_name'],))
                        orga_id = cursor.fetchone()[0]
                        add_oragnism(orga_id)
            except Exception as e:
                sg.popup(e)
            finally:
                cursor.close()
                connection.close()
                win["Plasmids.organism_selector"]('')
                db['Plasmids'].save_record(display_message=False)
                db['Plasmids'].set_by_pk(selected_plasmid)

    elif event == '-DESTROYORGA-':
        if values['Plasmids.destroyed'] == '':
            pass
        else:
            destruction_date = values['Plasmids.destroyed']
            selected_GMO = db['GMOs']['organism_id']
            gmo_summary = db['GMOs']['GMO_summary']
            selected_plasmid = db['Plasmids']['id']
            gmo_summary = gmo_summary.replace('tbd', destruction_date)
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("UPDATE GMOs SET GMO_summary = ? WHERE organism_id = ?", (gmo_summary, selected_GMO))
            connection.commit()
            cursor.close()
            connection.close()
            db['GMOs'].save_record(display_message=False)
            db['Plasmids'].set_by_pk(selected_plasmid)

### Attachments ###
    elif event == 'insElement':
        selected_plasmid = db['Plasmids']['id']
        db['Plasmids'].set_by_pk(selected_plasmid)
        attachment_path = sg.popup_get_file('Select a file')
        if attachment_path == '' or attachment_path == None:
            pass
        else:
            filename = os.path.basename(attachment_path)
            selected_plasmid=db['Plasmids']['id']
            if filename == '':
                sg.popup('Select a file.')
                db['Plasmids'].set_by_pk(selected_plasmid)
            else:
                insertBLOB(selected_plasmid, attachment_path, filename)
                db['Plasmids'].set_by_pk(selected_plasmid)
    elif event == '-ALIAS_IN-':
        selected_plasmid = db['Plasmids']['id']
        selected_cassette = db['Cassettes']['content']
        win['Plasmids.alias'].update(selected_cassette)
        db['Plasmids'].save_record(display_message=False)
        db['Plasmids'].set_by_pk(selected_plasmid)

### Genebank ###
    elif event == 'insGb':
        gb_path = sg.popup_get_file('Please choose a gb file.')
        if gb_path == '' or gb_path == None:
            pass
        else:
            Gb_filename = os.path.basename(gb_path)
            selected_plasmid=db['Plasmids']['id']
            if Gb_filename == '':
                sg.popup('Select a Gb file.')
            else:
                filename, file_extension = os.path.splitext(Gb_filename)
                if file_extension != '.gb' and file_extension != '.gbk':
                    sg.popup('File must have .gb or .gbk extension.')
                else:
                    try:
                        with open(gb_path, "r") as f:
                            data = f.read()
                        db['Plasmids'].set_by_pk(selected_plasmid)
                        win['Plasmids.genebank'](data)
                        win["Plasmids.gb_name"](Gb_filename)
                        win["Plasmids.gb"]('•')
                        db['Plasmids'].save_record(display_message=False)
                        db['Plasmids'].set_by_pk(selected_plasmid)
                    except Exception as e:
                        sg.popup(e)
                        print('Choose a text file.')
    elif event == '-info-':
        sg.popup('The names for the cassette elements must adhere to the entries in the glossary. They are case sensitive.\n\nThe only accepted seperator is "-" which must not be used in the glossary entries.',keep_on_top=True)
    
    ### File download ###
    elif event == '-down_gb-':
        try:
            download_path = 'Downloads/'
            name_file = db['Plasmids']['gb_name']
            if name_file != '':
                file= open(download_path + name_file, 'r+')
        except FileNotFoundError:
            if name_file != '':
                file= open(download_path + name_file, 'w+')
        except IsADirectoryError:
            sg.popup("There is no Genebank file to download.")
        except Exception as e:
            sg.popup(e)
        finally:
            if name_file != '':
                file.write(db['Plasmids']['genebank'])
                file.close()
            elif name_file == '':
                sg.popup("There is no Genebank file to download.")
    elif event == '-down_att-':
        try:
            att_id = db['Attachments']['attach_id']
            att_name = db['Attachments']['Filename']
            readBlobData(att_id, att_name)
        except Exception as e:
            sg.popup(e)

### autocomplete ###
    # pressing down arrow will trigger event -AIN- then aftewards event Down:
    elif event == '-ESCAPEKEY-':
        win['-AIN-'].update('')
        win['-BOX-CONTAINER-'].update(visible=False)
    elif event == '-DOWNKEY-' and len(prediction_list): 
        sel_item = (sel_item + 1) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
    elif event == '-UPKEY-' and len(prediction_list):
        sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
    elif event == '-ENTERKEY-':
        if len(values['-BOX-']) > 0:
            win['-AIN-'].update(value=values['-BOX-'])
            win['-BOX-CONTAINER-'].update(visible=False)
    elif event == '-AIN-':
        text = values['-AIN-'] if not values['-IGNORE CASE-'] else values['-AIN-'].lower()
        if text == input_text:
            continue
        else:
            input_text = text
        prediction_list = []
        if text:
            if values['-IGNORE CASE-']:
                prediction_list = [item for item in choices if item.lower().startswith(text)]
            else:
                prediction_list = [item for item in choices if item.startswith(text)]

        list_element.update(values=prediction_list)
        sel_item = 0
        list_element.update(set_to_index=sel_item)

        if len(prediction_list) > 0:
            win['-BOX-CONTAINER-'].update(visible=True)
        else:
            win['-BOX-CONTAINER-'].update(visible=False)
    elif event == '-BOX-':
        win['-AIN-'].update(value=values['-BOX-'])
        win['-BOX-CONTAINER-'].update(visible=False)
    elif event == '-ADDFEATURE-':
        selected_dropdown_feature = values['-AIN-']
        if selected_dropdown_feature[2:-3] in choices: # the truncation of values['-AIN-'][2:-3] is a hack to deal with the shape of 'choices' such as: ('Feature1'),
            selected_dropdown_feature = selected_dropdown_feature[2:-3]
        if selected_dropdown_feature == "":
            pass
        else:
            variant = '['+values['-VARIANT-']+']'
            if db['Cassettes']['content'] == 'Empty' or db['Cassettes']['content'] == '':
                if values['-VARIANT-'] != '':
                    win['Cassettes.content'].update(selected_dropdown_feature + variant)
                else:
                    win['Cassettes.content'].update(selected_dropdown_feature)
            elif values['-VARIANT-'] != '':
                win['Cassettes.content'].update(db['Cassettes']['content'] + '-' + selected_dropdown_feature + variant)
            else:
                win['Cassettes.content'].update(db['Cassettes']['content'] + '-' + selected_dropdown_feature)
            db['Cassettes'].save_record(display_message=False)
            win['-AIN-'].update('')
            win['-VARIANT-'].update('')
            check_features()
            check_organisms()

### Features ###
    elif event == '-ALLEXCEL-':
        connection = sqlite3.connect(database)
        pd.read_sql_query('SELECT * FROM Features', connection).to_excel('Downloads/ALL_nucleic_acid_features.xlsx', index=False, engine='xlsxwriter')
        connection.close()
        sg.popup('Done.')
    elif event == '-ALLEXCELORGA-':
        connection = sqlite3.connect(database)
        pd.read_sql_query('SELECT * FROM Organisms', connection).to_excel('Downloads/ALL_organisms.xlsx', index=False, engine='xlsxwriter')
        connection.close()
        sg.popup('Done.')
    elif event == '-USEDEXCEL-':
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Cassettes')
            lst = []
            for i in cursor.fetchall():
                lst.append(i[1])
            lst = '-'.join(lst).split('-')
            cursor.close()

            today = date.today()
            target = 'Downloads/USED_nucleic_acid_features' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'
            writer = pd.ExcelWriter(target, engine='xlsxwriter')
            # also drop id column here:
            pd.read_sql_query('SELECT annotation, alias, risk, organism FROM Features WHERE annotation IN {}'.format(str(tuple(lst))), connection).to_excel(writer, sheet_name='Sheet1', index=False, startrow=0)
            connection.close()

            workbook  = writer.book
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
            format = workbook.add_format({'text_wrap': True, 'border': 1})
            worksheet = writer.sheets['Sheet1']

            worksheet.write(0, 0, 'Annotation', header_format)
            worksheet.write(0, 1, 'Alias', header_format)
            worksheet.write(0, 2, 'Risk', header_format)
            worksheet.write(0, 3, 'Organism', header_format)

            footer = initials +' List of used nucleic acid features'
            worksheet.set_footer(footer)
            worksheet.set_portrait()
            worksheet.repeat_rows(0)
            worksheet.set_paper(9)
            worksheet.fit_to_pages(1, 0)  # 1 page wide and as long as necessary.

            worksheet.set_column(0, 0, 20, format)
            worksheet.set_column(1, 1, 60, format)
            worksheet.set_column(2, 2, 10, format)
            worksheet.set_column(3, 3, 10, format)

            writer.close()

            sg.popup('Done.')
        except:
            sg.popup('There must be more than one element in the list in order to use the export function.')
    elif event == '-USEDEXCELORGA-':
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()

            # find all features from cassettes
            cursor.execute('SELECT * FROM Cassettes')
            lst = []
            for i in cursor.fetchall():
                lst.append(i[1])
            lst = '-'.join(lst).split('-')

            # find all organism names from GMOs
            cursor.execute('SELECT * FROM GMOs')
            lst2 = []
            for i in cursor.fetchall():
                lst2.append(i[2])

            # find all organism short names in features for organisms in GMOs
            cursor.execute('SELECT short_name FROM Organisms WHERE full_name IN {}'.format(str(tuple(lst2))))
            lst3 = []
            for i in cursor.fetchall():
                lst3.append(i[0])

            # find all organism short names for used features
            cursor.execute('SELECT organism FROM Features WHERE annotation IN {}'.format(str(tuple(lst))))
            lst4 = []
            for i in cursor.fetchall():
                lst4.append(i[0])

            # combine all organism short names of features and GMOs
            lst5 = lst3 + lst4

            today = date.today()
            target = 'Downloads/USED_organisms' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'
            writer = pd.ExcelWriter(target, engine='xlsxwriter')

            pd.read_sql_query('SELECT full_name, short_name, RG FROM Organisms WHERE short_name IN {}'.format(str(tuple(lst5))), connection).to_excel(writer, sheet_name='Sheet1', index=False, startrow=0)
            cursor.close()
            connection.close()

            workbook  = writer.book
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
            format = workbook.add_format({'text_wrap': True, 'border': 1})
            worksheet = writer.sheets['Sheet1']

            worksheet.write(0, 0, 'Full name', header_format)
            worksheet.write(0, 1, 'Short name', header_format)
            worksheet.write(0, 2, 'Risk group', header_format)

            footer = initials +' List of used organisms'
            worksheet.set_footer(footer)
            worksheet.set_portrait()
            worksheet.repeat_rows(0)
            worksheet.set_paper(9)
            worksheet.fit_to_pages(1, 0)  # 1 page wide and as long as necessary.

            worksheet.set_column(0, 0, 50, format)
            worksheet.set_column(1, 1, 20, format)
            worksheet.set_column(2, 2, 10, format)

            writer.close()

            sg.popup('Done.')

        except:
            sg.popup('There must be more than one element in the list in order to use the export function.')

    elif event == '-IMPEXCEL-':
        try:
            wb = pd.read_excel('Downloads/templates/nucleic_acid_features.xlsx',sheet_name = 0)
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Features")
            cursor.execute("DELETE from sqlite_sequence where name='Features'")
            connection.commit()
            wb['annotation'] = wb['annotation'].replace('-', '_', regex=True)
            wb['annotation'] = wb['annotation'].replace('\[', '(', regex=True)
            wb['annotation'] = wb['annotation'].replace(']', ')', regex=True)
            wb  = wb.fillna(value='None')
            wb.to_sql(name='Features',con=connection,if_exists='append', index=False, index_label='id')
            connection.commit()
            connection.close()
            db['Features'].save_record(display_message=False)
            #problem here, table does not refresh, solution hack:
            #db['Features'].insert_record()
            #db['Features'].delete_record(ask=False)
            #better:
            db['Features'].requery()
            choices = autocomp()
        except FileNotFoundError:
            sg.popup('File Downloads/templates/nucleic_acid_features.xlsx does not exist.')
        else:
            source_dir = 'Downloads/templates/'
            try:
                os.unlink(os.path.join(source_dir, "nucleic_acid_features_imported.xlsx"))
            except OSError:
                pass
            os.rename(os.path.join(source_dir, 'nucleic_acid_features.xlsx'), os.path.join(source_dir, "nucleic_acid_features_imported.xlsx"))
            sg.popup('Downloads/templates/nucleic_acid_features.xlsx was renamed to nucleic_acid_features_imported.xlsx')
    elif event == '-IMPEXCELORGA-':
        try:
            wb = pd.read_excel('Downloads/templates/organisms.xlsx',sheet_name = 0)
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Organisms")
            cursor.execute("DELETE from sqlite_sequence where name='Organisms'")
            connection.commit()
            wb.to_sql(name='Organisms',con=connection,if_exists='append', index=False, index_label='id')
            connection.commit()
            connection.close()
            db['Organisms'].save_record(display_message=False)
            db['Organisms'].requery()
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        except FileNotFoundError:
            sg.popup('File Downloads/templates/organisms.xlsx does not exist.')
        else:
            source_dir = 'Downloads/templates/'
            try:
                os.unlink(os.path.join(source_dir, "organisms_imported.xlsx"))
            except OSError:
                pass
            os.rename(os.path.join(source_dir, 'organisms.xlsx'), os.path.join(source_dir, "organisms_imported.xlsx"))
            sg.popup('File Downloads/templates/organisms.xlsx was renamed to organisms_imported.xlsx')

    elif event == '-ADDEXCEL-':
        #TODO: file browse
        try:
            wb = pd.read_excel('Downloads/templates/nucleic_acid_features.xlsx',sheet_name = 0)
            add_to_features(wb)
            choices = autocomp()
        except FileNotFoundError:
            sg.popup('File Downloads/templates/nucleic_acid_features.xlsx does not exist.')
        else:
            source_dir = 'Downloads/templates/'
            try:
                os.unlink(os.path.join(source_dir, "nucleic_acid_features_imported.xlsx"))
            except OSError:
                pass
            os.rename(os.path.join(source_dir, 'nucleic_acid_features.xlsx'), os.path.join(source_dir, "nucleic_acid_features_imported.xlsx"))
            sg.popup('File Downloads/templates/nucleic_acid_features.xlsx was renamed to nucleic_acid_features_imported.xlsx')

    elif event == '-ADDGOOGLE-':
        try:
            #import ssl # import not here
            ssl._create_default_https_context = ssl._create_unverified_context #monkeypatch
            sheet_id = db['Settings']['gdrive_glossary']
            sheet_name = 'features'
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            wb = pd.read_csv(url)
            add_to_features(wb)
            choices = autocomp()
        except Exception as e:
            sg.popup(e)

    elif event == '-ADDEXCELORGA-': 
        #TODO: file browse
        try:
            wb = pd.read_excel('Downloads/templates/organisms.xlsx',sheet_name = 0)
            add_to_organisms(wb)
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        except FileNotFoundError:
            sg.popup('File Downloads/templates/organisms.xlsx does not exist.')
        except Exception as e:
            sg.popup(e)
        else:
            source_dir = 'Downloads/templates/'
            try:
                os.unlink(os.path.join(source_dir, "organisms_imported.xlsx"))
            except OSError:
                pass
            os.rename(os.path.join(source_dir, 'organisms.xlsx'), os.path.join(source_dir, "organisms_imported.xlsx"))
            sg.popup('File Downloads/templates/organisms.xlsx was renamed to organisms_imported.xlsx')

    elif event == '-ADDGOOGLEORGA-':
        try:
            sheet_id = db['Settings']['gdrive_glossary']
            sheet_name = 'organisms'
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            wb = pd.read_csv(url)
            add_to_organisms(wb)
            choices = autocomp()
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        except Exception as e:
            sg.popup(e)

    elif event == '-FEATUREINFO-':
        sg.popup('Dashes and brackets "-, [, ]" in annotation names are not allowed and will be replaces by underscores and parentheses "_, (, )".')
    elif event == '-FEATURECOMBO-':
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['Features.organism'].update(disabled=True) # not a perfect solution
            win['Features.organism'].update(value=values['-FEATURECOMBO-'])
    elif event == '-ADDSELORGA-':
            orga_selection = select_orga()
            win['-SETSELORGA-'].Update(values = orga_selection)
            if values['-SETSELORGA-'] != '':
                value="'{}'".format(values['-SETSELORGA-'])
                db['OrganismSelection'].insert_record(column='organism_name', value=value)
    elif event == '-COPYFAVORGA-':
        selected_orga = db['OrganismSelection']['organism_name']
        value="'{0}'".format(selected_orga)
        db['OrganismFavourites'].insert_record(column='organism_fav_name', value=value)

### Check features completeness ###
    elif event == '-CHECKFEATURES-':
        check = check_features()
        if check[0] == True:
            sg.popup('All used nucleic acid features are present in the glossary.')
        if len(check[1]) > 0:
            sg.popup('The following features in the Nucleic acids feature glossary are redundant (not used):\n', ", ".join(check[1]), '\n You can keep them or remove them.')
        if len(check[2]) > 0:
            sg.popup('The following duplications were found in the Nucleic acids feature glossary:\n', ", ".join(check[2]), '\n Please remove duplicated items!')

### Check organisms completeness ###
    elif event == '-CHECKORGANISMS-':
        check = check_organisms()
        if check[0] == True:
            sg.popup('All used organisms are present in the glossary.')
        if len(check[1]) > 0:
            sg.popup('The following organisms in the Organism glossary are redundant (not used):\n', ", ".join(check[1]), '\n You can keep them or remove them.')
        if len(check[2]) > 0:
            sg.popup('The following duplications were found in the Organism glossary:\n', " ,".join(check[2]), '\n Please remove duplicated items!')

### Check for duplicated plasmid names ###
    elif event == '-CHECKPLASMIDS-':
        check = check_plasmids()
        if len(check[0]) > 0:
            sg.popup('The following duplicated plasmid names were found:\n', ", ".join(check[0]), '\n Please fix!')
        if len(check[1]) > 0:
            sg.popup('The following plasmids have no original vector:\n', ", ".join(check[1]), '\n Please fix!')
        if len(check[2]) > 0:
            sg.popup('The following plasmids have no cassettes:\n', ", ".join(check[2]), '\n Please fix!')
        if len(check[3]) > 0:
            sg.popup('The following plasmids have no GMOs:\n', ", ".join(check[3]), '\n Please fix!')
        else:
            sg.popup('All good!')

### Upload to ICE ###
    elif event == '-ICE-':
        upload = sg.popup_yes_no('Dependind on the database size and internet connection it may take some time. Proceed?')
        if upload == 'Yes':
            upload_ice(thisice='')

### Formblatt Z ###
    elif event == '-FORMBLATT-':
        features_check = check_features()
        organisms_check = check_organisms()
        if features_check[0] == True and organisms_check[0] == True:
            formblatt = generate_formblatt()
            today = date.today()
            target = 'Downloads/Formblatt-Z' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'
            
            #unformatted
            #formblatt.to_excel('Downloads/Formblatt-Z' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '_unformatted.xlsx', index=False)

            #formatted
            writer = pd.ExcelWriter(target, engine='xlsxwriter')
            formblatt.to_excel(writer, sheet_name='Sheet1', header=False, index=False, startrow=1)
            # write header
            for colx, value in enumerate(formblatt.columns.values):
                writer.sheets['Sheet1'].write(0, colx, value)

            workbook  = writer.book
            worksheet = writer.sheets['Sheet1']

            footer = 'Formblatt Z, ' + institution
            worksheet.set_footer(footer)
            worksheet.set_landscape()
            worksheet.repeat_rows(0)
            worksheet.set_paper(9)
            worksheet.fit_to_pages(1, 0)  # 1 page wide and as long as necessary.
            
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
            format = workbook.add_format({'text_wrap': True, 'border': 1})

            for col_num, value in enumerate(formblatt.columns.values):
                worksheet.write(0, col_num, value, header_format)

            worksheet.set_column(0, 0, 4, format)
            worksheet.set_column(1, 1, 30, format)
            worksheet.set_column(2, 2, 12, format)
            worksheet.set_column(3, 3, 16, format)
            worksheet.set_column(4, 4, 9, format)
            worksheet.set_column(5, 5, 13, format)
            worksheet.set_column(6, 6, 28, format)
            worksheet.set_column(7, 7, 25, format)
            worksheet.set_column(8, 8, 15, format)
            worksheet.set_column(9, 9, 5, format)
            worksheet.set_column(10, 10, 9, format)
            worksheet.set_column(11, 11, 15, format)
            worksheet.set_column(12, 12, 13, format)
            worksheet.set_column(13, 13, 10, format)

            writer.close()
            sg.popup('Done.')

### Plasmid list ###
    elif event == '-PLASMIDLIST-':
        plasmidlist = generate_plasmidlist()
        today = date.today()
        target = 'Downloads/Plasmidlist' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'
        writer = pd.ExcelWriter(target, engine='xlsxwriter')
        plasmidlist.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook  = writer.book
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
        format = workbook.add_format({'text_wrap': True, 'border': 1})
        worksheet = writer.sheets['Sheet1']
        footer = initials +' Plasmidlist, date: ' + str(today.strftime("%Y-%m-%d"))
        worksheet.set_footer(footer)
        worksheet.set_landscape()
        worksheet.repeat_rows(0)
        worksheet.set_paper(9)
        worksheet.fit_to_pages(1, 0)  # 1 page wide and as long as necessary.

        # format header
        for col_num, value in enumerate(plasmidlist.columns.values):
            worksheet.write(0, col_num, value, header_format)

        worksheet.set_column(0, 0, 6, format)
        worksheet.set_column(1, 1, 14, format)
        worksheet.set_column(2, 2, 60, format)
        worksheet.set_column(3, 3, 6, format)
        worksheet.set_column(4, 4, 14, format)
        worksheet.set_column(5, 5, 60, format)
        worksheet.set_column(6, 6, 60, format)
        worksheet.set_column(7, 7, 10, format)
        worksheet.set_column(8, 8, 10, format)

        writer.close()
        sg.popup('Done.')

### Import data ###
    elif event == '-IMPORTGMOCU-':
        import_data()
        db=ss.Database(database, win,  sql_script=sql_script)
        choices = autocomp()
        orga_selection = select_orga()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)

### Info in settings ###
    elif event == '-SETTINGSINFO-':
        sg.popup(version)

    elif event == '-CTRL-E-':
        win['Settings.scale'].update(disabled=False)
        win['Settings.font_size'].update(disabled=False)

### Exit ###
    elif event == sg.WIN_CLOSED or event == 'Exit':
        l = read_settings()
        user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client = l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13]
        sg.user_settings_set_entry('-THEME-', style)
        sg.user_settings_set_entry('-SCALE-', float(scale))
        sg.user_settings_set_entry('-FONTSIZE-', int(font_size))
        db=None              # <= ensures proper closing of the sqlite database and runs a database optimization
        break