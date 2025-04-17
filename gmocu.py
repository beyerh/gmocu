#!/usr/bin/python3

appname  = 'GMOCU'
version_no  = float(0.73)
vdate    = '2025-04-07'
database = 'gmocu.db'

# TODO:
### Future features
# Implement generating GMOs with multiple plasmids
# Better implementation for uploading new/modified plasmid entries

### Bugs
# Better progress bar for Filebrowser upload?
# Check what setting 'upload completed' does

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
import shutil
from pathlib import Path
from datetime import date
from fuzzywuzzy import process, fuzz
import asyncio
from filebrowser_client import FilebrowserClient
import gspread
from gspread_dataframe import get_as_dataframe
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
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

# set appdir path
user_data = os.sep.join([str(Path.home()), 'GMOCU'])

# copy template files if path does not yet exist
try:
    source = os.sep.join([os.getcwd(), 'Downloads', 'templates'])
    target = os.sep.join([user_data, 'templates'])
    templates_path = shutil.copytree(source, target, dirs_exist_ok=False)
except FileExistsError:
    pass

# set settings path
SETTINGS_PATH = user_data
sg.user_settings_filename(path=SETTINGS_PATH)

### autocomplete ###
orga_selection = []

# PySimpleGUI standard font size
os_font_size = 13
os_scale_factor = 1

# PySimpleGUI layout code
font_size = sg.user_settings_get_entry('-FONTSIZE-', os_font_size)
scale_factor = sg.user_settings_get_entry('-SCALE-', os_scale_factor)
if sys.platform.startswith("linux"):
    horizontal_layout = sg.user_settings_get_entry('-HORIZONTAL-', 0)
else:
    horizontal_layout = sg.user_settings_get_entry('-HORIZONTAL-', 1)
sg.set_options(font=("Helvetica", font_size))
#sg.theme('DarkBlack')
sg.theme(sg.user_settings_get_entry('-THEME-', 'Reddit'))  # set the theme

img_base64 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAABeAAAAXgH42Q/5AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAPtJREFUOI3tkjFKAwEQRd/fDZZCMCcQRFRCCi1SWdmksNDCC1jmAlmt0mRbsbDyAKKQQkstbAVtXG3EIwhpDRi/jcuuWTesvb+bYd5n+DOyTZl0+NzlEzteOymdKTNQL9kk0DUQYHccN28qGyhKFgl0h2l8t0YwaXvQepmeDQpw/3Ue6SoHA9RxeKkoqc800N5FyPv4DFgtrsUy0rn6t7XyDZZWjpE7BTjTFuOFox++aQY6eNoHTmfAmaxuehnZzic+V8kAPtLLiN7jdOJVNYJJu0agHdAQpeu5AeyWQEOkt6wMtwt/oChZR7r/Fbc3HDcf8q3CH/xV/wbwBe0pVw+ecPjyAAAAAElFTkSuQmCC'
img2_base64 = b'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAUCAYAAABSx2cSAAAACXBIWXMAAAJhAAACYQHBMFX6AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAOhJREFUOI3tz79OwlAUx/HvJTe1gW5iOqohcZHJuLv6Gs6uLvgADsbFGGZeQx+ADafqoEhiY4wabUyg/PFAexl0acCLneU3npzPOfkpaoEhT8RZM2dbHwAawNWKyqpjNeHnmFjSzEwDbPsurcOKFe83Hrlqx7MYIBokrJ/e/YpHk592KxKq4xuTwcZAX1JcrfA9Pf/Cd4ovvQmSGGa29jZLXB5sWCvs1jtcPw8pWLcWZIn/EQ5eR+xcPOTGGuhLYnjqjhVQzIXNSdUDUEf3ZRx5z/s5k2Y4oHretqJOJPNxLCm3b19/+jwFyitLV/vbA1oAAAAASUVORK5CYII='

# fix os-specific glitches
headings=[' ID ','  Name  ','                     Alias                       ','  Status  ','G '] # Table column widths can be set by the spacing of the headings!
features_headings = ['ID   ','   Annotation    ','                 Alias                 ','   Risk   ', 'Organism']
organisms_headings = ['ID   ','                  Full name                    ','      Short name     ','RG    ']
alias_length = 59
plasmid_titles_size = 14
features_titles_size = 15
if horizontal_layout == 0:
    plasmid_table_rows = 12
    features_table_rows = 38
    organisms_table_rows = 40
    plasmid_summary_lines = 4
    plasmid_purpose_lines = 4
else:
    plasmid_table_rows = 47
    features_table_rows = 40
    organisms_table_rows = 42
    plasmid_summary_lines = 8
    plasmid_purpose_lines = 5
    


if sys.platform == "win32":
    headings=['ID',' Name ','            Alias            ','Status','G '] # Table column widths can be set by the spacing of the headings!
    features_headings = ['ID ','Annotation','        Alias        ','Risk', 'Organism']
    organisms_headings = ['ID','           Full name          ','Short name ','RG']
    alias_length = 59
    plasmid_titles_size = 14
    features_titles_size = 15
    if horizontal_layout == 1:
        plasmid_table_rows = 40
        features_table_rows = 33
        organisms_table_rows = 35
        plasmid_summary_lines = 5
        plasmid_purpose_lines = 3

elif sys.platform.startswith("linux"):  # could be "linux", "linux2", "linux3", ...
    headings=['ID','       Name       ','                                                      Alias                                                    ','        Status        ',' G   '] # Table column widths can be set by the spacing of the headings!
    features_headings = ['ID ','         Annotation               ','                                        Alias                                      ','       Risk       ', '     Organism         ' ]
    organisms_headings = ['ID','                                                          Full name                                                       ','   Short name             ',' RG      ']
    plasmid_titles_size = 16
    features_titles_size = 17
    alias_length = 57
    os_font_size = 13
    os_scale_factor = 1.6
    if horizontal_layout == 1:
        plasmid_table_rows = 40
        features_table_rows = 35
        organisms_table_rows = 36
        plasmid_summary_lines = 4
        plasmid_purpose_lines = 4
        plasmid_summary_lines = 6
        plasmid_purpose_lines = 5

##### Plasmid data #####
visible=[0,1,1,1,1] # Hide the primary key column in the table

record_columns=[
    [sg.Column([
        [sg.Text('Plasmid name:', size=(plasmid_titles_size,1))],
        [sg.Text('          ', key='-SPACEREF-')],
        [sg.Text('', key='-TEXTLEN-')]
    ], vertical_alignment='top', pad=(0,0))]+
    [sg.Column([
        ss.record('Plasmids.name',no_label=True,size=(35,10))+
        [sg.T("Clone:")]+
        ss.record('Plasmids.clone',no_label=True, size=(5,10))+
        ss.record('Plasmids.gb',no_label=True, visible=False, size=(0,10))+
        ss.record('Plasmids.date',no_label=True, readonly=True, size=(10,10)), # invisible
        ss.selector('cassettesSelector','Cassettes',size=(61,4)),
    ], pad=(0,0))],
    [sg.Column([
        [sg.Text('Cassette:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    [sg.Column([
        ss.record('Cassettes.content',no_label='True',size=(46,10),)+
        [sg.Button('!', key='-info-', size=(1, 1)),]+
        ss.actions('cassettesActions','Cassettes', edit_protect=False, navigation=False, save=True, search=False),
    ], pad=(0,0))],
    # autocomplete
    [sg.Column([
        [sg.Text('Add Feature:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    [sg.Column([
        [sg.Combo(size=(25, 1), enable_events=True, key='-AIN-', values=[], disabled=True)] +
        [sg.Text('Variant:')]+
        [sg.Input(size=(20, 1), key='-VARIANT-', disabled=True)]+
        [sg.Button(' ', image_data=img_base64, button_color = (sg.theme_background_color(), sg.theme_background_color()), key='-ADDFEATURE-')],
    ], pad=(0,0))],
    [sg.Column([
        [sg.Text('Alias:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Plasmids.alias',no_label=True,size=(alias_length,10))+[sg.Button('+', key='-ALIAS_IN-', size=(1, 1)),],
    [sg.Column([
        [sg.Text('Purpose:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Plasmids.purpose',sg.MLine, (61, plasmid_purpose_lines),no_label=True),
    [sg.Column([
        [sg.Text('Cloning summary:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Plasmids.summary',sg.MLine, (61, plasmid_summary_lines),no_label=True),
    [sg.Column([
        [sg.Text('Orig. vector:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Plasmids.backbone_vector',no_label=True, size=(29,10))+
    [sg.Text('Status:', pad=(1,0), justification='center')] + ss.record('Plasmids.status',no_label=True, element=sg.Combo, quick_editor=False, size=(18,10))+
    ss.actions('plasmidActions','Plasmids', edit_protect=False,navigation=False,save=True, search=False, insert=False, delete=False),
    
   #[sg.Col([[sg.Text('GMOs:' + spacer3),]],vertical_alignment='t')] + ss.selector('gmoSelector','GMOs', size=(61,5)), #better for Windows
    [sg.Column([
        [sg.Text('GMOs:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+ 
    ss.selector('gmoSelector','GMOs', size=(61,5)), #better for macOS
   #[sg.T('                              '),] + ss.selector('gmoSelector', 'GMOs', element=sg.Table, headings=['ID', 'GMO_summary', 'Organism         ','Plasmid ID','Target RG', 'Date generated', 'Date destroyed'], visible_column_map=[0,0,1,0,1,1,1],num_rows=5),
    [sg.Column([
        [sg.Text('Organism selector:', size=(plasmid_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+ 
    [sg.Column([
        ss.record('Plasmids.organism_selector',element=sg.Combo, quick_editor=False, no_label=True, size=(24,10),)+
        [sg.T('Target RG:'),]+
        ss.record('Plasmids.target_RG',size=(3,10), no_label=True)+
        [sg.T('Approval: '),] + [sg.Input('-', size=(9,10), key='-APPROVAL-')],
        [sg.T('Made / Destroyed:'),] + ss.record('Plasmids.generated',size=(10,10), no_label=True) +
        ss.record('Plasmids.destroyed',size=(10,10), no_label=True)+
        [sg.Button('Add', key='-ADDORGA-', size=(3, 1)),]+
        [sg.Button(':)', key='-ADDFAV-', size=(1, 1)),]+
        ss.actions('GMOActions','GMOs', edit_protect=False,navigation=False,save=False, search=False, insert=False)+
        [sg.Button('Destroy', key='-DESTROYORGA-', size=(6, 1)),],
    ], pad=(0,0))],
]

selectors=[
    ss.actions('plasmidActions','Plasmids',search_size=(27, 1)) + [sg.Button('', image_data=img2_base64, button_color = (sg.theme_background_color(), sg.theme_background_color()), key='-DUPLICATE-')]+
    [sg.Button('UP', key='-THISICE-', size=(3, 1)),],
    ss.selector('tableSelector', 'Plasmids', element=sg.Table, headings=headings, visible_column_map=visible,num_rows=plasmid_table_rows), #15 rows
]

sub_genebank = [ 
    [sg.Text(size=(plasmid_titles_size-1,1))]+
    ss.record('Plasmids.gb_name', no_label=True, size=(42,10))+
    [sg.Col([[sg.Button('+', key='insGb', size=(1, 1))]], element_justification="center", key='-GENEBANKCOL-')]+
    [sg.Button('Download', key='-down_gb-', size=(8, 1))]+
    ss.record('Plasmids.genebank',no_label=True, size=(1,10)),
]

tablayout_attach = [
    
    [sg.T(size=(plasmid_titles_size-1,1))]+
    ss.selector('attachmentSelector','Attachments', size=(39,4))+
    [sg.Col([],size=(0,0), element_justification="center", vertical_alignment="center", key='-ATTACHCOL-')]+
    [sg.Button('+', key='insElement', size=(1, 1))]+
    ss.actions('attachmentActions','Attachments',edit_protect=False,navigation=False,save=False,search=False,insert=False)+
    [sg.Button('Download', key='-down_att-', size=(8, 1))]
]

record_columns += [[sg.Frame('Genebank', sub_genebank, key='-GENEBANKFRAME-')]]
record_columns += [[sg.Frame('Attachments', tablayout_attach, key='-ATTACHFRAME-')]]

# without frame
if horizontal_layout == 0:
    tablayout_plasmid = selectors + record_columns
else:
    tablayout_plasmid = [ [sg.Column(selectors, vertical_alignment='top'), sg.VSeparator(), sg.Column(record_columns, vertical_alignment='center')], ]

##### GMO #####
tablayout_GMO = [
    [sg.Text('Maintenance')],
    [sg.Button('Run', key='-CHECKFEATURES-'),] + [sg.Text('Check Nucleic acid feature glossary completeness')],
    [sg.Button('Run', key='-CHECKORGANISMS-'),] + [sg.Text('Check Organisms glossary completeness')], 
    [sg.Button('Run', key='-CHECKPLASMIDS-'),] + [sg.Text('Check for plasmid duplications and completeness')],
    [sg.Text('')],
    [sg.Text('JBEI/ice, Filebrowser, GDrive')], 
    [sg.Button('Run', key='-SERVERS-')] + [sg.Text('Upload/update all plasmid information, gb files to JBEI/ice, and with attachements to\nGDrive, Filebrowser server, as configured.')] + [sg.CB('Only new plasmids', default=False, k='-ONLYNEW-', visible=False)], # for now invisible to remove it, might put it back later
    [sg.Text('')],
    [sg.Text('GMO')], 
    [sg.Button('Run', key='-PLASMIDLIST-'),] + [sg.Text('Generate plasmid list')],
    [sg.Button('Run', key='-FORMBLATT-'),] + [sg.Text('Generate Formblatt Z')],
    [sg.Text('')],
    [sg.Text('Data import')],
    [sg.Button('Run', key='-IMPORTGMOCU-'),] + [sg.Text('Import data from another gmocu database file')],
    #[sg.Output(size=(78, 20))],
]

##### Features #####
tablayout_Features = [
    ss.selector('featureSelector', 'Features', element=sg.Table, headings=features_headings , visible_column_map=[0,1,1,1,1],num_rows=features_table_rows),
    ss.actions('featureActions','Features'),
    [sg.Column([
        [sg.Text('Annotation:', size=(features_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Features.annotation',no_label=True, enable_events=True, size=(62,10)),
    [sg.Column([
        [sg.Text('Alias:', size=(features_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Features.alias',no_label=True,size=(62,10)),
    [sg.Column([
        [sg.Text('Risk:', size=(features_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    ss.record('Features.risk',no_label=True,size=(62,10)),
    #ss.record('Features.organism', element=sg.Combo, label='Organism:',size=(62,10)),
    [sg.Column([
        [sg.Text('Organism:', size=(features_titles_size,1))]
    ], vertical_alignment='top', pad=(0,0))]+
    [sg.Combo(orga_selection, size=(26,10), enable_events=True, key='-FEATURECOMBO-')]+
    ss.record('Features.organism', no_label=True, size=(32,10))]

tablayout_Features_controls = [
    [sg.Button('Export all to Excel', key='-ALLEXCEL-')] +
    [sg.Button('Export used to Excel', key='-USEDEXCEL-')] +
    [sg.Button('Import from Excel', key='-ADDFEATURESEXCEL-')] +
    [sg.Button('Online sync', key='-FEATURESYNC-')]+
    [sg.Button('!', key='-FEATUREINFO-')],
]
if horizontal_layout == 0:
    tablayout_Features += tablayout_Features_controls
else:
    tablayout_Features = [ [sg.Column(tablayout_Features, vertical_alignment='top'), sg.VSeparator(), sg.Column(tablayout_Features_controls, vertical_alignment='top')], ]

##### Organisms #####
tablayout_Organisms = [
    ss.selector('organismSelector', 'Organisms', element=sg.Table, headings=organisms_headings , visible_column_map=[0,1,1,1],num_rows=organisms_table_rows),
    ss.actions('organismActions','Organisms'),
    #ss.record('Organisms.id',label='ID:',size=(62,10)),
    ss.record('Organisms.full_name',label='Full name:',size=(62,10)),
    ss.record('Organisms.short_name', label='Short name:',size=(62,10)),
    ss.record('Organisms.RG',label='RG:',size=(62,10))]
tablayout_Organisms_controls = [
    [sg.Button('Export all to Excel', key='-ALLEXCELORGA-')] +
    [sg.Button('Export used to Excel', key='-USEDEXCELORGA-')] +
    [sg.Button('Import from Excel', key='-ADDEXCELORGA-')] +
    [sg.Button('Online sync', key='-ORGASYNC-')],
]
if horizontal_layout == 0:
    tablayout_Organisms += tablayout_Organisms_controls
else:
    tablayout_Organisms = [ [sg.Column(tablayout_Organisms, vertical_alignment='top'), sg.VSeparator(), sg.Column(tablayout_Organisms_controls, vertical_alignment='top')], ]

##### Settings #####
tablayout_Settings_1 = [
    ss.record('Settings.name',label='Name:', size=(62,10)),
    ss.record('Settings.initials',label='Initials:', size=(62,10)),
    ss.record('Settings.email',label='Email:', size=(62,10)),
    ss.record('Settings.institution',label='GMO institute:', size=(62,10)),
    ss.record('Settings.ice',label='Server credentials:', element=sg.Combo, size=(56,10)),
    ss.record('Settings.gdrive_glossary',label='GDrive Sheet ID:', size=(62,10)),
    ss.record('Settings.gdrive_id',label='GDrive Folder ID:', size=(62,10)),
    [sg.Text("Style*:                   ")] + [sg.Col([[sg.Combo(['Reddit', 'DarkBlack', 'Black', 'BlueMono', 'BrownBlue', 'DarkBlue', 'LightBlue', 'LightGrey6'], default_value=sg.user_settings_get_entry('-THEME-', 'Reddit'), size=(60,10), enable_events=True, key='-SETSTYLE-')]], vertical_alignment='t')],
    ss.record('Settings.style',no_label=True, size=(29,10)),   
]

tablayout_Settings_2 = [
    ss.record('Settings.scale',label='Scale factor*:', size=(62,10)),
    ss.record('Settings.font_size',label='Font size*:', size=(62,10)),
    
    [sg.Col([
        ss.record('Settings.horizontal_layout',label='Horizontal layout*:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.duplicate_gmos',label='Duplicate GMOs:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.upload_completed',label='Upload completed:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.autosync',label='Autosync GSheets:', element=sg.CBox, size=(1,1))
    ], pad=(0,0), expand_x=True)]+
    #ss.record('Settings.upload_abi',label='Upload .ab1 files:', element=sg.CBox),
    [sg.Col([
        ss.record('Settings.use_ice',label='Use JEBI/ice:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.use_filebrowser',label='Use Filebrowser:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.use_gdrive',label='Use GDrive Folder:', element=sg.CBox, size=(1,1)),
        ss.record('Settings.zip_files',label='    Zip files (faster):', element=sg.CBox, size=(1,1))
    ], pad=(0,0), expand_x=True)],
    [sg.Text('If both JBEI/ice and Filebrowser are used, a link to the Filebrowser folder will be added to each\n JBEI/ice entry.')],
    [sg.Text('*Restart required')],
]

tablayout_Settings_TargetOrganisms = [
    [sg.Text('Target organisms: ')] +
    [sg.Col([ss.selector('organismselectionSelector','OrganismSelection',size=(60,7)),
    [sg.Combo(orga_selection, size=(30,10), enable_events=True, key='-SETSELORGA-')]+
    [sg.Button('Add', key='-ADDSELORGA-')]+
    ss.actions('organismselectionActions','OrganismSelection', edit_protect=False, navigation=False, save=False, search=False, insert=False)], vertical_alignment='t')],
]

tablayout_Settings_FavOrganisms = [
    [sg.Text('Fav. organisms:    ')] +
    [sg.Col([ss.selector('favouritesSelector','OrganismFavourites',size=(60,6)),
    [sg.Button('Copy', key='-COPYFAVORGA-')]+
    ss.actions('favouritesselectionActions','OrganismFavourites', edit_protect=False, navigation=False, save=False, search=False, insert=False)], vertical_alignment='t')],
    [sg.Text('                                  All listed organisms must also exist in Target organisms.')],
]

if horizontal_layout == 0:
    tablayout_Settings = [ss.actions('settingsActions','Settings', edit_protect=True,navigation=False,save=True, search=False, insert=False, delete=False) + [sg.Button('Info', key='-SETTINGSINFO-'),] + ss.record('Settings.version',no_label=True, readonly=True, visible=False, size=(0,0))] + tablayout_Settings_1 + tablayout_Settings_2 + tablayout_Settings_TargetOrganisms + tablayout_Settings_FavOrganisms
else:
    tablayout_Settings = [
    ss.actions('settingsActions','Settings', edit_protect=True,navigation=False,save=True, search=False, insert=False, delete=False) + [sg.Button('Info', key='-SETTINGSINFO-'),] + ss.record('Settings.version',no_label=True, readonly=True, visible=False, size=(0,0)), # invisible,
    [sg.Column(tablayout_Settings_1, vertical_alignment='top')]+[sg.Column(tablayout_Settings_2, vertical_alignment='top')],                  
    [sg.Column(tablayout_Settings_TargetOrganisms, vertical_alignment='top')]+[sg.Column(tablayout_Settings_FavOrganisms, vertical_alignment='top')],
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
win=sg.Window('GMOCU - GMO Documentation', layout, scaling=scale_factor, return_keyboard_events=True, finalize=True)
win['Plasmids.gb_name'].update(disabled=True)
win['Plasmids.gb'].update(disabled=True)
win['Plasmids.genebank'].update(visible=False)
win['Settings.style'].update(visible=False)
win['-ATTACHFRAME-'].expand(True, True)
win['-GENEBANKFRAME-'].expand(True, True)
win.refresh()
win['-ATTACHCOL-'].expand(True, True)
win['-ATTACHCOL-'].contents_changed()
win['-GENEBANKCOL-'].expand(True, True)
win.refresh()
win.move_to_center()
win.refresh()

# update database path for use with appdirs
database = os.sep.join([user_data, database])
# check if database file already exists for version maintainance below
database_file_exists = os.path.isfile(database)

sql_script ='gmocu.sql'
# generate database
db=ss.Database(database, win,  sql_script=sql_script) #<=== Here is the magic!
# Note:  sql_script is only run if *.db does not exist!  This has the effect of creating a new blank
# database as defined by the sql_script file if the database does not yet exist, otherwise it will use the database!

# Maintain db changes in version updates, try altering existing Settings table, skip if the file was freshly generated
if database_file_exists == True:
    connection = sqlite3.connect(database) 
    cursor = connection.cursor()
    database_was_changed = False
    try:
        db_saved_version = db['Settings']['version']
    except:
        db_saved_version = 0
    try:
        if db_saved_version < 0.5:
            settings_columns = [i[1] for i in cursor.execute('PRAGMA table_info(Settings)')]
            if not "version" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN version FLOAT DEFAULT 0;")
                database_was_changed = True
            if not "horizontal_layout" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN horizontal_layout INTEGER DEFAULT 0;")
                database_was_changed = True
                if sys.platform == "win32":
                    win['Settings.horizontal_layout'].update(1)
                    db['Settings'].save_record(display_message=False)
                    cursor.execute("UPDATE Settings SET horizontal_layout = 1;")
        
        if db_saved_version < 0.6:
            credentials_columns = [i[1] for i in cursor.execute('PRAGMA table_info(IceCredentials)')]
            if not "filebrowser_instance" in credentials_columns:
                add_columns = ['filebrowser_instance', 'filebrowser_user', 'filebrowser_pwd']
                for i in add_columns:
                    cursor.execute("ALTER TABLE IceCredentials ADD COLUMN {} TEXT;".format(i))
                database_was_changed = True
            settings_columns = [i[1] for i in cursor.execute('PRAGMA table_info(Settings)')]
            if not "use_ice" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN use_ice INTEGER DEFAULT 1;")
                database_was_changed = True
            if not "use_filebrowser" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN use_filebrowser INTEGER DEFAULT 1;")
                database_was_changed = True

        if db_saved_version < 0.7:
            # adding uid, workaround to create new tabe because of alter table error: sqlite3.OperationalError: Cannot add a column with non-constant default
            # also changing risk DEFAULT from "None" to "No Risk" in table Features because of interference during sync with "None" values.
            features_columns = [i[1] for i in cursor.execute('PRAGMA table_info(Features)')]
            organisms_columns = [i[1] for i in cursor.execute('PRAGMA table_info(Organisms)')]
            settings_columns = [i[1] for i in cursor.execute('PRAGMA table_info(Settings)')]
            if not "uid" in features_columns or not "uid" in organisms_columns:
                # make a backup
                name = 'gmocu_backup_{}.db'.format(str(date.today().strftime("%Y-%m-%d")))
                path = os.sep.join([user_data, name])

                def progress(status, remaining, total):
                    print(f'Copied {total-remaining} of {total} pages...')

                dst = sqlite3.connect(path)
                with dst:
                    connection.backup(dst, pages=1, progress=progress)
                dst.close()
            if not "uid" in features_columns:
                cursor.execute("CREATE TABLE Features_new(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, annotation TEXT, alias TEXT, risk TEXT DEFAULT 'No Risk', organism TEXT, uid CHAR(16) NOT NULL DEFAULT (lower(hex(randomblob(16)))));")
                decision = sg.popup_yes_no('The table with the Nucleic acid features is being modified to work with Google Sheets. It is recommended to import them fresh from the shared glossary. Do you still want to keep your entries and assign them uniqe IDs (you will find a backup in the GMOCU folder in any case)?')
                if decision == 'Yes':
                    cursor.execute("INSERT INTO Features_new(id, annotation, alias, risk, organism) SELECT id, annotation, alias, risk, organism FROM Features;")
                cursor.execute("DROP TABLE Features;")
                cursor.execute("ALTER TABLE Features_new RENAME TO Features;")
                database_was_changed = True
            if not "synced" in features_columns:
                cursor.execute("ALTER TABLE Features ADD COLUMN synced INTEGER DEFAULT 0;")
                database_was_changed = True
            if not "uid" in organisms_columns:
                cursor.execute("CREATE TABLE Organisms_new(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, full_name TEXT, short_name TEXT, RG TEXT, uid CHAR(16) NOT NULL DEFAULT (lower(hex(randomblob(16)))));")
                decision = sg.popup_yes_no('The table with the Organisms definitions is being modified to work with Google Sheets. It is recommended to import them fresh from the shared glossary. Do you still want to keep your entries and assign them uniqe IDs (you will find a backup in the GMOCU folder in any case)?')
                if decision == 'Yes':
                    cursor.execute("INSERT INTO Organisms_new(id, full_name, short_name, RG) SELECT id, full_name, short_name, RG FROM Organisms;")
                cursor.execute("DROP TABLE Organisms;")
                cursor.execute("ALTER TABLE Organisms_new RENAME TO Organisms;")
                database_was_changed = True
            if not "synced" in organisms_columns:
                cursor.execute("ALTER TABLE Organisms ADD COLUMN synced INTEGER DEFAULT 0;")
                database_was_changed = True
            if not "use_gdrive" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN use_gdrive INTEGER DEFAULT 0;")
                database_was_changed = True
            if not "gdrive_id" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN gdrive_id TEXT DEFAULT 'ID from link';")
                database_was_changed = True
            if not "zip_files" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN zip_files INTEGER DEFAULT 1;")
                database_was_changed = True
            if not "autosync" in settings_columns:
                cursor.execute("ALTER TABLE Settings ADD COLUMN autosync INTEGER DEFAULT 0;")
                database_was_changed = True

        if database_was_changed:
            sg.popup('The database file structure has been updated. Please restart GMOCU.')
            
            
        # write current version to db file    
        if db_saved_version < version_no:
            if db_saved_version < 0.5:
                cursor.execute("UPDATE Settings SET version = {};".format(version_no))
            else:
                win['Settings.version'].update(version_no)
                db['Settings'].save_record(display_message=False)    
        
                        
    except Exception as e:
        sg.popup(e)
        pass
    finally:
        cursor.close()
        connection.commit()
        connection.close()


#db['Plasmids'].set_order_clause('ORDER BY id ASC')
db['Cassettes'].set_order_clause('ORDER BY cassette_id ASC')
db['Plasmids'].set_search_order(['name','alias']) # the search box will search in both the name and example columns
db['Features'].set_search_order(['annotation','alias', 'organism']) # the search box will search in both the name and example columns
db.edit_protect()
selected_plasmid=db['Plasmids']['id']
db['Plasmids'].set_by_pk(selected_plasmid)

# disable extra elements
extra_el_disabled = True
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
win['Settings.gdrive_id'].update(disabled=True)
win['Settings.style'].update(disabled=True)
win['-SETSTYLE-'].update(disabled=True)
win['Settings.scale'].update(disabled=True)
win['Settings.font_size'].update(disabled=True)
win['Settings.horizontal_layout'].update(disabled=True)
win['Settings.duplicate_gmos'].update(disabled=True)
win['Settings.upload_completed'].update(disabled=True)
#win['Settings.upload_abi'].update(disabled=True)
win['Settings.use_ice'].update(disabled=True)
win['Settings.use_filebrowser'].update(disabled=True)
win['Settings.use_gdrive'].update(disabled=True)
win['Settings.zip_files'].update(disabled=True)
win['Settings.autosync'].update(disabled=True)
win['-SETSELORGA-'].update(disabled=True)
win['-ADDSELORGA-'].update(disabled=True)
win['-COPYFAVORGA-'].update(disabled=True)
win['-ADDFAV-'].update(disabled=True)

# keyboard navigation
win.bind('<Down>', '-DOWNKEY-')
win.bind('<Up>', '-UPKEY-')
win.bind('<Return>', '-ENTERKEY-')
win.bind('<Escape>', '-ESCAPEKEY-')
win.bind('<Button-1>', '-LEFTCLICK-')
win.bind('<Control-KeyPress-e>', '-CTRL-E-') # trigger event with key press combination

### read settings ###
def read_settings():
    ice = db['Settings']['ice']
    connection = sqlite3.connect(database)
    settings = pd.read_sql_query("SELECT * FROM Settings", connection)
    credits = pd.read_sql_query("SELECT * FROM IceCredentials WHERE id = {}".format(ice), connection)
    connection.close()

    user_name               = settings['name'][0]
    initials                = settings['initials'][0]
    email                   = settings['email'][0]
    ice                     = settings['ice'][0]
    institution             = settings['institution'][0]
    duplicate_gmos          = settings['duplicate_gmos'][0]
    upload_completed        = settings['upload_completed'][0]
    upload_abi              = settings['upload_abi'][0]
    scale                   = settings['scale'][0]
    font_size               = settings['font_size'][0]
    style                   = settings['style'][0]
    horizontal_layout       = settings['horizontal_layout'][0]    

    ice_instance            = credits['ice_instance'][0]
    ice_token               = str(credits['ice_token'][0])
    ice_token_client        = credits['ice_token_client'][0]
    filebrowser_instance    = credits['filebrowser_instance'][0]
    filebrowser_user        = credits['filebrowser_user'][0]
    filebrowser_pwd         = credits['filebrowser_pwd'][0]
    use_ice                 = settings['use_ice'][0]
    use_filebrowser         = settings['use_filebrowser'][0]
    use_gdrive              = settings['use_gdrive'][0]
    zip_files               = settings['zip_files'][0]
    autosync                = settings['autosync'][0]

    return user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync

user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync = read_settings()

### GUI settings ###
if scale == '__':
    scale = os_scale_factor
if font_size == '__':
    font_size = os_font_size
    win['Settings.font_size'].update(font_size)
    win['Settings.scale'].update(scale)
    if not sys.platform.startswith("linux"):
        win['Settings.horizontal_layout'].update(1)
    else:
        win['Settings.horizontal_layout'].update(0)
    db['Settings'].save_record(display_message=False)    

sg.user_settings_set_entry('-THEME-', style)
sg.user_settings_set_entry('-SCALE-', float(scale))
sg.user_settings_set_entry('-FONTSIZE-', int(font_size))
sg.user_settings_set_entry('-HORIZONTAL_LAYOUT-', int(win['Settings.horizontal_layout'].get()))

### autocomplete ###
def autocomp():
    try:
        connection = sqlite3.connect(database) 
        cursor = connection.cursor()
        choices = [job[0] for job in cursor.execute("SELECT annotation FROM Features")]
        cursor.close()
        connection.close()
        return sorted(choices)
    except Exception as e:
        sg.popup(e)

### organism drop down ###
def select_orga():
    try:
        connection = sqlite3.connect(database) 
        cursor = connection.cursor()
        orga_selection = [job[0] for job in cursor.execute("SELECT short_name FROM Organisms")]
        cursor.close()
        connection.close()
        return sorted(orga_selection)
    except Exception as e:
        sg.popup(e)

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

def readBlobData(attId, attName, path):
    try:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        path = path
        with open(os.sep.join([path, attName]), "wb") as output_file:
            cursor.execute("SELECT file FROM Attachments WHERE attach_id = ?", (attId,))
            ablob = cursor.fetchall()
            #sg.popup("ablob ", len(ablob))
            output_file.write(ablob[0][0])

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    except IsADirectoryError:
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
    wb['annotation'] = wb['annotation'].replace(' ', '_', regex=True)
    redundant_entries = wb[wb["annotation"].isin(annots)]["annotation"]
    sg.popup('The following entries already exist and will not be imported:\n\n{}'.format(', '.join(redundant_entries.tolist())))
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
    
    
def update_cassettes(old2new_annot_dict):
    connection = sqlite3.connect(database)
    cursor2 = connection.cursor()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Cassettes") 
    for row in cursor:
        for key, val in old2new_annot_dict.items():
            if key in row[1]:
                #print('Found ', key, ' in', row[1])
                key = re.sub('\(', '\(', key)
                key = re.sub('\)', '\)', key)
                new_content = re.sub('(?<=-)'+key+'(?=[-[])', val, '-'+row[1]+'-').strip('-')
                cursor2.execute('UPDATE Cassettes SET content=? WHERE cassette_id=?', (new_content, row[0]))
    connection.commit()
    connection.close()

def update_alias(old2new_annot_dict):
    connection = sqlite3.connect(database)
    cursor2 = connection.cursor()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Plasmids") 
    for row in cursor:
        print(row)
        for key, val in old2new_annot_dict.items():
            if row[2] not in ['', None]:
                if key in row[2]:
                    #print('Found ', key, ' in', row[2])
                    key = re.sub('\(', '\(', key)
                    key = re.sub('\)', '\)', key)
                    new_content = re.sub('(?<=-)'+key+'(?=[-[])', val, '-'+row[2]+'-').strip('-')
                    #print('new content ', new_content)
                    cursor2.execute('UPDATE Plasmids SET alias=? WHERE id=?', (new_content, row[0]))
    connection.commit()
    connection.close()
    db['Plasmids'].requery()

def sync_gsheets():
    #todo ignore if uid '', necessary?
    credits = os.sep.join([user_data, 'gmocu_gdrive_credits.json'])
    sheet_id = db['Settings']['gdrive_glossary']
    connection = sqlite3.connect(database)

    glossary_features = pd.read_sql_query("SELECT * FROM Features ", connection)
    glossary_organisms = pd.read_sql_query("SELECT * FROM Organisms ", connection)

    if not os.path.isfile(credits) or sheet_id == None or sheet_id == '' or sheet_id == 'ID from link':  # check if service accout credis exist
        sg.popup("Please setup the access to the Google Sheets online glossaries.\n\nFollow the instructions at https://github.com/beyerh/gmocu. Add the Sheet ID in the Settings and save the file 'gmocu_gdrive_credits.json' to your GMOCU folder.")

    elif glossary_features.isnull().any().any() or (glossary_features.eq("")).any().any():
        sg.popup("Empty fields in the Nucleic acids features glossary detected. Please fill all fields first to sync complete data with the online glossary.")
    elif glossary_organisms.isnull().any().any() or (glossary_organisms.eq("")).any().any():
        sg.popup("Empty fields in the Organisms glossary detected. Please fill all fields first to sync complete data with the online glossary.")

    else:
        try:
            gc = gspread.service_account(filename=credits)
            sheet = gc.open_by_key(sheet_id)
        except gspread.exceptions.SpreadsheetNotFound:
            sg.popup('The spreadsheet with ID\n\n{}\n\ncould not be found.\nDid you share it with write permissions with the service account mentioned in the gmocu_gdrive_credits.json file?'.format(sheet_id))

        # create three worksheets in case they are not there yet
        try:
            features_sheet = sheet.worksheet("features")
        except gspread.exceptions.WorksheetNotFound:
            features_sheet = sheet.add_worksheet(title="features", rows=1000, cols=5)
            features_sheet_headers = pd.DataFrame(columns=['annotation', 'alias', 'risk', 'organism', 'uid', 'valid'])
            features_sheet.update([features_sheet_headers.columns.values.tolist()])
        try:
            organisms_sheet = sheet.worksheet("organisms")
        except gspread.exceptions.WorksheetNotFound:
            organisms_sheet = sheet.add_worksheet(title="organisms", rows=1000, cols=4)
            organisms_sheet_headers = pd.DataFrame(columns=['full_name', 'short_name', 'RG', 'uid', 'valid'])
            organisms_sheet.update([organisms_sheet_headers.columns.values.tolist()])
        try:
            logging_sheet = sheet.worksheet("logging")
        except gspread.exceptions.WorksheetNotFound:
            logging_sheet = sheet.add_worksheet(title="logging", rows=5000, cols=4)
            logging_sheet_headers = pd.DataFrame(columns=['item', 'user', 'date', 'action'])
            logging_sheet.update([logging_sheet_headers.columns.values.tolist()])

        ### First, check for new online entries to import into the local table
        # get online values as dataframe and remove empty rows
        online_features = get_as_dataframe(features_sheet).dropna(how='all')
        valid_online_features = online_features[online_features['valid'] == 1]
        online_organisms = get_as_dataframe(organisms_sheet).dropna(how='all')
        valid_online_organisms = online_organisms[online_organisms['valid'] == 1]

        # get local features
        try:
            local_features = pd.read_sql_query('SELECT * FROM Features', connection)
            local_organisms = pd.read_sql_query('SELECT * FROM Organisms', connection)

            # online features without matching uid in local features (online features not in local), reset index numbers
            new_online_features = online_features[~online_features['uid'].isin(local_features['uid'])].reset_index(drop=True)
            new_online_organisms = online_organisms[~online_organisms['uid'].isin(local_organisms['uid'])].reset_index(drop=True)

            # remove rows which were set as invalid with the value other than 1
            valid_new_online_features = new_online_features[new_online_features['valid'] == 1]
            valid_new_online_organisms = new_online_organisms[new_online_organisms['valid'] == 1]

            # import including the UID to keep that entry unique across all instances
            cursor = connection.cursor()
            for idx, feature in valid_new_online_features.iterrows():
                cursor.execute("INSERT INTO Features (annotation, alias, risk, organism, uid, synced) VALUES (?, ?, ?, ?, ?, ?)", (feature['annotation'], feature['alias'], feature['risk'], feature['organism'], feature['uid'], 1))
            connection.commit()
            for idx, organism in valid_new_online_organisms.iterrows():
                #cursor.execute("INSERT INTO Organisms (full_name, short_name, RG, uid, synced) VALUES (?, ?, ?, ?, ?)", (organism['full_name'], organism['short_name'], int(float(organism['RG'])), organism['uid'], 1))
                cursor.execute("INSERT INTO Organisms (full_name, short_name, RG, uid, synced) VALUES (?, ?, ?, ?, ?)", (organism['full_name'], organism['short_name'], str(organism['RG']), organism['uid'], 1))
            connection.commit()

            if len(valid_new_online_features.index) > 0:
                    sg.popup('The following freatures were imported:\n', ', '.join(valid_new_online_features['annotation']))
            if len(valid_new_online_organisms.index) > 0:
                    sg.popup('The following organisms were imported:\n', ', '.join(valid_new_online_organisms['short_name']))

        except Exception as e:
            sg.popup(e)

        ### Second, append new local entries to the onine table
        try:
            # get and raise a warning on local entries with the same annotation or short name as one in the online glossary
            repeated_annotations = list(local_features[local_features['annotation'].isin(online_features['annotation'])&(local_features['synced']==0)]['annotation'])
            if repeated_annotations:
                sg.popup('The following locally stored features have an annotation name that already exists in the Google Sheets glossary:\n\n' + ', '.join(repeated_annotations) + '\n\nThese features will therefore not be uploaded nor synced to the online glossary. This also means you will have duplicate features in your local database; please remove them as soon as possible.')
            repeated_organisms = list(local_organisms[local_organisms['short_name'].isin(online_organisms['short_name'])&(local_organisms['synced']==0)]['short_name'])
            if repeated_organisms:
                sg.popup('The following locally stored organisms have an short name that already exists in the Google Sheets glossary:\n\n' + ', '.join(repeated_organisms) + '\n\nThese organisms will therefore not be uploaded nor synced to the online glossary. This also means you will have duplicate organisms in your local database; please remove them as soon as possible.')
            # get local entries which not exist with the same UID online and with a different annotation, remove unnecessary columns
            new_local_features = local_features[~(local_features['uid'].isin(online_features['uid'])|local_features['annotation'].isin(online_features['annotation']))].reset_index(drop=True).drop('id', axis=1)
            new_local_organisms = local_organisms[~(local_organisms['uid'].isin(online_organisms['uid'])|local_organisms['short_name'].isin(online_organisms['short_name']))].reset_index(drop=True).drop('id', axis=1)
            # chance synced in all rows to 1 (will be uploaded as "valid")
            new_local_features.loc[:,'synced'] = 1
            new_local_organisms.loc[:,'synced'] = 1
            # convert dataframe to list and use append rows of gspread
            data_list_features = new_local_features.values.tolist()
            features_sheet.append_rows(data_list_features)

            data_list_organisms = new_local_organisms.values.tolist()
            organisms_sheet.append_rows(data_list_organisms)

            # log upload online
            logging_list = []
            for i in new_local_features['annotation'].tolist():
                logging_list.append([i, initials, date.today().strftime('%Y-%m-%d'), 'added'])
            for i in new_local_organisms['short_name'].tolist():
                logging_list.append([i, initials, date.today().strftime('%Y-%m-%d'), 'added'])
            
            logging_sheet.append_rows(logging_list)

            # store synced value 1 in local tables
            for idx, feature in new_local_features.iterrows():
                cursor.execute('UPDATE Features SET synced=? WHERE uid=?', (1, feature['uid']))
            connection.commit()
            for idx, organism in new_local_organisms.iterrows():
                cursor.execute('UPDATE Organisms SET synced=? WHERE uid=?', (1, organism['uid']))
            connection.commit()

            if len(new_local_features.index) > 0:
                    sg.popup('The following freatures were uploaded:\n', ', '.join(new_local_features['annotation']))
            if len(new_local_organisms.index) > 0:
                    sg.popup('The following organisms were uploaded:\n', ', '.join(new_local_organisms['short_name']))

        except Exception as e:
            sg.popup(e)
                
        ### Third, check for values such as names or definitions that have changed in the online table and update the local feature table, also apply the changes to the already used Cassettes
        try:
            local_features = pd.read_sql_query('SELECT * FROM Features', connection) # update values after import
            local_organisms = pd.read_sql_query('SELECT * FROM Organisms', connection) # update values after import
            local_features_comparison = local_features.drop(columns=['id', 'synced'], axis=1).sort_values(by=['uid'],ignore_index=True)
            local_organisms_comparison = local_organisms.drop(columns=['id', 'synced'], axis=1).sort_values(by=['uid'],ignore_index=True)
            online_features_comparison = valid_online_features.drop('valid', axis=1).sort_values(by=['uid'],ignore_index=True)
            online_organisms_comparison = valid_online_organisms.drop('valid', axis=1).sort_values(by=['uid'],ignore_index=True)
            online_organisms_comparison[['RG']] = online_organisms_comparison[['RG']].astype(str) # convert column to str to match comparison below


            updated_features = []
            if not online_features_comparison.equals(local_features_comparison): # calculate difference only if they are not a perfect match
                # get the rows with entries that have modifications online
                online_features_comparison.set_index(list(online_features_comparison.columns), inplace=True)
                local_features_comparison.set_index(list(local_features_comparison.columns), inplace=True)
                online_modified_features = online_features_comparison[~online_features_comparison.index.isin(local_features_comparison.index)].reset_index()

                # update online changes in database Features table
                for idx, row in online_modified_features.iterrows():
                    updated_features.append(row['annotation'])
                    cursor.execute('UPDATE Features SET annotation=?, alias=?, risk=?, organism=? WHERE uid=?', (row['annotation'], row['alias'], row['risk'], row['organism'], row['uid']))
                connection.commit()

                # exchange the the annotation names if they have changed in all cassettes
                previous_annotations_of_online_mod_features = local_features[local_features['uid'].isin(online_modified_features['uid'])]

                # gererate dict with previous, new paired colums
                previous_new_dict = dict(zip(previous_annotations_of_online_mod_features['annotation'], online_modified_features['annotation']))
                #print('oldnew\n', previous_new_dict)

                # update modified annotation names in cassettes
                update_cassettes(previous_new_dict)

                # update Alias in Plasmids as well
                update_alias(previous_new_dict)

                if len(updated_features) > 0:
                    sg.popup('The following freatures were updated:', ', '.join(updated_features))

            updated_organisms = []
            if not online_organisms_comparison.equals(local_organisms_comparison): # calculate difference only if they are not a perfect match
                # get the rows with entries that have modifications online
                online_organisms_comparison.set_index(list(online_organisms_comparison.columns), inplace=True)
                local_organisms_comparison.set_index(list(local_organisms_comparison.columns), inplace=True)
                online_modified_organisms = online_organisms_comparison[~online_organisms_comparison.index.isin(local_organisms_comparison.index)].reset_index()
                online_modified_organisms[['RG']] = online_modified_organisms[['RG']].astype(str) # convert to str

                # update online changes in database Features table
                for idx, row in online_modified_organisms.iterrows():
                    updated_organisms.append(row['short_name'])
                    cursor.execute('UPDATE Organisms SET full_name=?, short_name=?, RG=? WHERE uid=?', (row['full_name'], row['short_name'], row['RG'], row['uid']))
                connection.commit()

                if len(updated_organisms) > 0:
                    sg.popup('The following organisms were updated:', ', '.join(updated_organisms))

        except Exception as e:
            sg.popup(e)

        ### Fourth, delete local entries which were set as invalid online
        try:
            # Features
            invalid_online_features = online_features[online_features['valid'] != 1].drop('valid', axis=1).sort_values(by=['uid'],ignore_index=True)
            local_features_valid_invalid = local_features.drop(columns=['id', 'synced'], axis=1).sort_values(by=['uid'],ignore_index=True)
            invalid_local_features = pd.DataFrame().reindex_like(local_features_valid_invalid).dropna()
            
            for idx, row in local_features_valid_invalid.iterrows():
                if row['uid'] in invalid_online_features.uid.values:
                    invalid_local_features = pd.concat([invalid_local_features, pd.DataFrame([row])], ignore_index=True)

            if len(invalid_local_features.index) > 0:
                del_invalid = sg.popup_yes_no('The following Nucleic acid Features were set as "invalid" in the Google Sheet master glossary and will be deleted. You may need to fix it.\n\n{}\n\nProceed?'.format(', '.join(invalid_local_features['annotation'].tolist())))
                if del_invalid == 'Yes':
                    for idx, feature in invalid_local_features.iterrows():
                        cursor.execute("DELETE FROM Features WHERE uid=?", (feature['uid'],))
            connection.commit()

            # Organisms
            invalid_online_organisms = online_organisms[online_organisms['valid'] != 1].drop('valid', axis=1).sort_values(by=['uid'],ignore_index=True)
            local_organisms_valid_invalid = local_organisms.drop(columns=['id', 'synced'], axis=1).sort_values(by=['uid'],ignore_index=True)
            invalid_local_organisms = pd.DataFrame().reindex_like(local_organisms_valid_invalid).dropna()

            for idx, row in local_organisms_valid_invalid.iterrows():
                if row['uid'] in invalid_online_organisms.uid.values:
                    invalid_local_organisms = pd.concat([invalid_local_organisms, pd.DataFrame([row])], ignore_index=True)

            if len(invalid_local_organisms.index) > 0:
                del_invalid = sg.popup_yes_no('The following Organisms were set as "invalid" in the Google Sheet master glossary and will be deleted. You may need to fix it.\n\n{}\n\nProceed?'.format(', '.join(invalid_local_organisms['short_name'].tolist())))
                if del_invalid == 'Yes':
                    for idx, feature in invalid_local_organisms.iterrows():
                        cursor.execute("DELETE FROM Organisms WHERE uid=?", (feature['uid'],))
            connection.commit()

        except Exception as e:
            sg.popup(e)
        
        finally:
            connection.close()
            db['Features'].requery()
            db['Organisms'].requery()
            db['Cassettes'].requery()
            db['Plasmids'].requery()

def generate_formblatt(lang):

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

        if lang == 'en':
            fZ_data.columns = ['No', 'Donor designation', 'Donor RG', 'Recipient designation', 'Recipient RG', 'Source vector designation', 'Transferred nucleic acid designation', 'Transferred nucleic acid risk potential', 'GMO name', 'GMO RG', 'GMO approval', 'GMO generated', 'GMO disposal', 'Entry date']
            
        return(fZ_data)

    except Exception as e:
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        sg.popup("Line: ", line, e)

def generate_plasmidlist():

    pL_data = pd.DataFrame({'No.':[],'Plasmid name':[],'Alias':[],'Clone':[],'Original vector':[],'Purpose':[],'Cloning summary':[],'Status':[],'Entry date':[]})

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

        row = {'No.':no,'Plasmid name':name,'Alias':alias,'Clone':clone,'Original vector':original_vector,'Purpose':purpose,'Cloning summary':summary,'Status':status,'Entry date':date}
        
        pL_data = pd.concat([pL_data, pd.DataFrame.from_records([row])], ignore_index=True)
        
    return(pL_data)

def upload_ice(thisice, use_ice):

    if use_ice == 0 and thisice == '':
        return
    else:

        try:
            user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync = read_settings()
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

            layout = [[sg.Text('Uploading plasmids to ICE...', key="uploader")],
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
                                
                                # create link if Filbrowser is used as well (unfortunately not clickable)
                                if use_filebrowser == 1:
                                    filebrowser_link = os.sep.join([filebrowser_instance, initials, ice_p['name']])
                                    ice.set_part_custom_field(ice_p['id'], 'Filebrowser link', filebrowser_link)

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
  
def upload_file_servers(thisfile, use_filebrowser, use_gdrive, zip_files):

    try:
        connection = sqlite3.connect(database)
        ### condition to overwrite local_plasmids here for THISICE button. Only upload/update the currently selected button.
        if thisfile != '':
            local_plasmids = pd.read_sql_query("SELECT * FROM Plasmids WHERE name = (?)", connection, params=(thisfile,))
        else:
            local_plasmids = pd.read_sql_query("SELECT * FROM Plasmids ", connection)
        status_values = pd.read_sql_query("SELECT * FROM SelectionValues ", connection)
        cassettes =  pd.read_sql_query("SELECT * FROM Cassettes ", connection)
        
        # Make local folder to collect data to upload, rename existing to backup location
        if thisfile != '':
            path = os.sep.join([user_data, initials, thisfile])
        else:
            path = os.sep.join([user_data, initials])
        if os.path.isdir(path):  # delete folder if it exists already
            shutil.rmtree(path) 
        print(path)
        Path(path).mkdir(parents=True, exist_ok=True) # create folder if not existing

        for idx, plasmid in local_plasmids.iterrows():

            if plasmid['name'] == 'p' + initials + '000' or '(Copy)' in plasmid['name']:
                sg.popup("Plasmid name '" + plasmid['name'] + "' is not allowed, no upload. Please change the name.")
                #sg.popup(plasmid['name'], plasmid['status'], ' not completed, no upload')

            else:
                print('Saving local plasmid data ' + plasmid['name'] + ' for Filebrowser/GDrive...')
                # Make subfolder for each plasmid
                if thisfile != '':
                    subfolder_path = path
                else:
                    subfolder_path = os.sep.join([path,  plasmid['name']])

                Path(subfolder_path).mkdir(parents=True, exist_ok=True)
                
                data =  "\n".join([
                    'Plasmid name: ' + plasmid['name'],
                    'Clone: ' + plasmid['clone'],
                    'Alias: ' + plasmid['alias'],
                    'Status: ' + status_values['value'][plasmid['status']-1],
                    'Short description: ' + plasmid['purpose'],
                    'Cloning: ' + plasmid['summary'],
                    'Backbone: ' + plasmid['backbone_vector'],
                    'Creator: ' + user_name,
                    'Creator email: ' + email,
                    'Entry date: ' + plasmid['date']                    
                    ])
                
                my_cassettes = cassettes[cassettes['plasmid_id']==plasmid['id']]['content']
                for idx, cassette in enumerate(my_cassettes):
                    data = "\n".join([data, 'Cassette {}: '.format(idx+1) + cassette])
                    #ice.set_part_custom_field(ice_p['id'], 'Cassette {}'.format(idx+1), cassette)

                with open(os.sep.join([subfolder_path, plasmid['name'] + ".txt"]), "w") as text_file:
                    text_file.write(data)

                if plasmid['genebank'] not in ('', None):
                    with open(os.sep.join([subfolder_path, plasmid['name'] + ".gb"]), "w") as gb_file:
                        gb_file.write(plasmid['genebank'])

                attachemtent_ids = pd.read_sql_query('SELECT attach_id, Filename FROM Attachments WHERE plasmid_id = {}'.format(plasmid['id']), connection)
                for idx, row in  attachemtent_ids.iterrows():
                    readBlobData(row['attach_id'], row['Filename'], subfolder_path)

        # Upload to Filebrowser server given in the settings
        if use_filebrowser == 1:
            client = FilebrowserClient(filebrowser_instance, filebrowser_user, filebrowser_pwd)
            asyncio.run(client.connect())

            if thisfile != '':
                deletepath = os.sep.join([initials, thisfile])
            else:
                deletepath = initials

            try:
                asyncio.run(client.delete(deletepath))
            except:
                pass
            
            # progress bar
            layout = [[sg.Text('Uploading plasmids to Filebrowser...', key="uploader")],
            [sg.ProgressBar(max_value=2, orientation='h', size=(20, 20), key='progress')]]
            upwin = sg.Window('GDrive Upload', layout, finalize=True)
            # Get the element to make updating easier
            progress_bar = upwin['progress']
            progress_bar.update_bar(1) 

            asyncio.run(client.upload(path, initials, override=True))
            progress_bar.update_bar(2)
            upwin.close()

            sg.popup('Upload to Filebrowser server completed.')

        # Upload to Google Drive folder
        if use_gdrive == 1:
            credits = os.sep.join([user_data, 'gmocu_gdrive_credits.json'])
            gauth = GoogleAuth()
            #scope = ["https://www.googleapis.com/auth/drive.file"]
            scope = ["https://www.googleapis.com/auth/drive"]
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(credits, scope)
            drive = GoogleDrive(gauth)

            # account info
            '''
            about = drive.GetAbout()
            print('Current user name:{}'.format(about['name']))
            print('Root folder ID:{}'.format(about['rootFolderId']))
            print('Total quota (bytes):{}'.format(about['quotaBytesTotal']))
            print('Used quota (bytes):{}'.format(about['quotaBytesUsed']))
            file_list = drive.ListFile().GetList()
            for file1 in file_list:
                print('title: %s, id: %s' % (file1['title'], file1['id']))
            '''

            # contact gdrive
            gdrive_folder_id = db['Settings']['gdrive_id']
            folderlist = drive.ListFile  ({'q': "'%s' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"% gdrive_folder_id}).GetList()
            
            # get initials folder id of existing folder and delete it if thisfile == ''
            if len(folderlist) > 0:
                for folder in folderlist:
                    if folder['title'] == initials:
                        initials_folder_id = folder['id']
                        if thisfile == '':
                            delfile = drive.CreateFile({'id':folder['id']})
                            delfile.Delete()

            # create a new initials folder
            if thisfile == '': 
                initials_folder = drive.CreateFile({'title': initials, 'parents':[{'id':gdrive_folder_id}], 'mimeType': 'application/vnd.google-apps.folder'})
                initials_folder.Upload()
                initials_folder_id = initials_folder['id']
                        
            # get path for progress
            if thisfile == '':
                dir = sorted(os.listdir(os.sep.join([user_data, initials])))
            else:
                dir = [thisfile]

            # progress bar
            layout = [[sg.Text('Uploading plasmids to GDrive folder...', key="uploader")],
            [sg.ProgressBar(max_value=len(dir), orientation='h', size=(20, 20), key='progress')]]
            upwin = sg.Window('GDrive Upload', layout, finalize=True)
            # Get the element to make updating easier
            progress_bar = upwin['progress']

            if thisfile != '': # delete plasmid folder or plasmid zip file instead
                plasmidfolder_and_zipfilelist = drive.ListFile  ({'q': "'%s' in parents and trashed=false"% initials_folder_id}).GetList()
                for item in plasmidfolder_and_zipfilelist:
                    if os.path.splitext(item['title'])[0] == thisfile:
                        delfile = drive.CreateFile({'id':item['id']})
                        delfile.Delete()
            
            # Zip files Settings option
            count = 0
            if zip_files == 1:
                for file in dir:
                    zip_content = shutil.make_archive(os.sep.join([user_data, initials, file]), 'zip', os.sep.join([user_data, initials, file]))
                    zipfile = drive.CreateFile({'parents':[{'id':initials_folder_id}]})
                    zipfile.SetContentFile(zip_content)
                    zipfile.Upload()
                    count += 1
                    upwin.Element('uploader').Update('Uploading ' + file)
                    progress_bar.update_bar(count)           
            
            else:
                for file in dir:
                    subfolder = drive.CreateFile({'title': file, 'parents':[{'id':initials_folder_id}], 'mimeType': 'application/vnd.google-apps.folder'})
                    subfolder.Upload()
                    count += 1
                    upwin.Element('uploader').Update('Uploading ' + file)
                    progress_bar.update_bar(count)
                    subfolder_id = subfolder['id']
                    for root,d_names,f_names in os.walk(os.sep.join([user_data, initials, file])):
                        for item in f_names:
                            upload_file = drive.CreateFile({'parents':[{'id':subfolder_id}]})
                            upload_file.SetContentFile(os.sep.join([root, item]))
                            upload_file.Upload()
            upwin.close()
            sg.popup('Upload to GDrive server completed completed.')

        if use_filebrowser == 0 and use_gdrive == 0:
            sg.popup('Files were only stored locally and not uploaded.')

    except Exception as e:
        sg.popup(e)
    
    finally:
        connection.close()

def add_organism(organism_index):
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
    if not file:
        return
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
                path = os.sep.join([user_data, name])

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
        features_columns = [i[1] for i in cursor.execute('PRAGMA other.table_info(Features)')]

        missing_features = np.setdiff1d(unique_imported_features, features_list) # yields the elements in `unique_imported_features` that are NOT in `features_list`
        nouid = False
        if len(missing_features) > 0:
            sg.popup('The following Nucleic acid features are missing and will be imported:\n', ', '.join(missing_features))
            for i in missing_features:
                print('Adding nucleic acid feature ', i)
                if not "uid" in features_columns:
                    nouid = True
                    cursor.execute("INSERT INTO Features (annotation, alias, risk, organism) SELECT annotation, alias, risk, organism FROM other.Features WHERE other.Features.annotation = ?", (i,))
                else:
                    cursor.execute("INSERT INTO Features (annotation, alias, risk, organism, uid) SELECT annotation, alias, risk, organism, uid FROM other.Features WHERE other.Features.annotation = ?", (i,))
            connection.commit()
            # replace None values if exist
            cursor.execute("UPDATE Features SET risk = REPLACE(risk, 'None', 'No Risk')"),
            connection.commit()

        # generate empty dataframes in case there are no features to import at all
        missing_organisms_from_features = pd.DataFrame(columns=['organism'])
        missing_organisms_from_gmos = pd.DataFrame(columns=['organism_name'])
        if len(missing_features) > 0:
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
        # Are any of the unique_missing_organisms alrady existing in the local file? Drop if so.
        local_organisms = pd.read_sql_query('SELECT short_name FROM Organisms', connection)
        for organism in unique_missing_organisms[:]: # iterrate throug a copy of the list ([:])
            if organism in local_organisms.short_name.values:
                unique_missing_organisms.remove(organism)

        organisms_columns = [i[1] for i in cursor.execute('PRAGMA other.table_info(Organisms)')]
        if len(unique_missing_organisms) > 0:
            sg.popup('The following Organisms are used by the imported nucleic acid features and generated GMOs but are missing and will be added:\n', ', '.join(unique_missing_organisms))
            for i in unique_missing_organisms:
                print('Adding organism ', i)
                if not "uid" in organisms_columns:
                    nouid = True
                    cursor.execute("INSERT INTO Organisms (full_name, short_name, RG) SELECT full_name, short_name, RG FROM other.Organisms WHERE other.Organisms.short_name = ?", (i,))
                else:
                    cursor.execute("INSERT INTO Organisms (full_name, short_name, RG, uid) SELECT full_name, short_name, RG, uid FROM other.Organisms WHERE other.Organisms.short_name = ?", (i,))
            connection.commit()

        if nouid:
            sg.popup('Features/Organisms were imported with new unique identifiers.')

        cursor.close()
        connection.close()

    except Exception as e:
        sg.popup(e)

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
        gmo_pids = list(gmo_pids['plasmid_id'])
        for pid in plasmid_ids:
            if pid not in gmo_pids:
                plasmid_wo_gmos.append(plasmids[plasmids['id']==pid]['name'].values[0])
        
        return [dupes, plasmids_wo_backbone, plasmid_wo_cassettes, plasmid_wo_gmos]

    except Exception as e:
        sg.popup(e)
    finally:
        connection.close()

def check_features():
    try:
        connection = sqlite3.connect(database)
        glossary_features = pd.read_sql_query("SELECT * FROM Features ", connection)

        if glossary_features.isnull().any().any() or (glossary_features.eq("")).any().any():
            sg.popup("Empty fields in the Nucleic acid features glossary detected. Please fill all fields.")

        glossary_features = list(glossary_features['annotation'])
        # check for duplicates in glossary_features
        seen = set()
        dupes = [x for x in glossary_features if x in seen or seen.add(x)]
        db_cassette_plasmid_data = pd.read_sql_query("SELECT content, plasmid_id FROM Cassettes ", connection)
        plasmid_ids = list(db_cassette_plasmid_data['plasmid_id'])
        #print(plasmid_ids)
        used_cassettes = list(db_cassette_plasmid_data['content'])
        # remove variants in []
        used_cassettes = [re.sub('\[.*?]', '', cassette) for cassette in used_cassettes]
        total_used_features = []
        missing_features = []
        for i in range(len(used_cassettes)):
            used_features = used_cassettes[i].split('-')
            total_used_features += used_features
            comparison = np.setdiff1d(used_features, glossary_features) # yields the elements in `used_features` that are NOT in `glossary_features
            plasmid_name = pd.read_sql_query("SELECT name,id FROM Plasmids WHERE id = {}".format(plasmid_ids[i]), connection)['name'][0]
            #print(plasmid_ids[i], plasmid_name)
            for element in comparison:
                missing_features.append(plasmid_name + ': ' + element)
        redundant = np.setdiff1d(glossary_features, total_used_features)
        nonmissing = ''
        if len(missing_features) == 0:
            nonmissing = True
        else:
            sg.popup('The following features are used in the cassettes of the listed plasmids, but missing in the "Nucleic acids" feature glossary:\n', '\n'.join(missing_features), '\nPlease check if there are no misspells and, if not, add them to the glossary!', title='Features missing!')

        return [nonmissing, redundant, dupes]
    #except Exception as e:
        #sg.popup(e)
    except Exception as e:
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        sg.popup("Line: ", line, e)
    finally:
        connection.close()

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
        # check for duplicates in organissm_glossary_list
        seen = set()
        dupes = [x for x in organissm_glossary_list if x in seen or seen.add(x)]
        missing_feature_organisms = np.setdiff1d(used_organisms_list, organissm_glossary_list)
        missing_feat_org_pairs = []
        for index, row in feature_organisms.iterrows():
            if row['organism'] in missing_feature_organisms:
                missing_feat_org_pairs.append(row['annotation'] + ': ' + row['organism'])
        redundant = np.setdiff1d(organissm_glossary_list, used_organisms_list)
        nonmissing = ''
        if len(missing_feature_organisms) == 0:
            nonmissing = True
        else:
            sg.popup('The following organisms are associated with used Nucleic Acids features, but missing in the "Organisms" glossary:\n', "\n".join(missing_feat_org_pairs), '\nPlease check if there are no misspells and, if not, add them to the glossary!', title='Organisms missing!')
        return [nonmissing, redundant, dupes]
    except Exception as e:
        sg.popup(e)
    finally:
        connection.close()

### autocomplete ###
def handler(event):
    num_opt = int((win.mouse_location()[1] - active_element.TooltipObject.tipwindow.winfo_y()) / (active_element.TooltipObject.tipwindow.winfo_height()/len(active_element.Values)))
    active_element.set_focus()
    active_element.Widget.event_generate('<Down>')
    active_element.update(set_to_index=num_opt)
    
def clear_combo_tooltip(ui_handle: sg.Element) -> None:
    if tt := ui_handle.TooltipObject:
        tt.hidetip()
        ui_handle.TooltipObject = None

def show_combo_tooltip(ui_handle: sg.Element, tooltip: [str], space_ref: sg.Element, text_len: sg.Element) -> None:
    max_len = 0
    for i in tooltip:
        text_len.update(i)
        win.refresh()
        if text_len.get_size()[0] > max_len:
            max_len = text_len.get_size()[0]
    text_len.update('')
    win.refresh()
    
    handle_width = ui_handle.get_size()[0]
    space_width = space_ref.get_size()[0]/10
    tooltip = "\n".join([i + " "*round((handle_width - max_len)/space_width) for i in tooltip])
    ui_handle.set_tooltip(tooltip)
    tt = ui_handle.TooltipObject
    tt.widget.unbind("<Enter>")
    tt.widget.unbind("<Leave>")
    tt.y += 40
    tt.showtip()
    tt.tipwindow.bind('<Button-1>', handler)
    

def autocomplete(event: str, event_data: dict[str, str], auto_options: list[str], ui_handle: sg.Element, space_ref: sg.Element, text_len: sg.Element) -> None:
    new_text = event_data[ui_handle.key]
    if new_text == '':
        if auto_options['show_on_empty']:
            sym = auto_options['values']
        else:
            sym = []
    else:
        matches = process.extractBests(new_text, auto_options['values'], scorer=lambda x,y:fuzz.ratio(x,y)+40*y.lower().startswith(x.lower()), score_cutoff=45, limit=10)
        sym = [m[0] for m in matches]
    clear_combo_tooltip(ui_handle=ui_handle)  
    ui_handle.update(new_text, values=sym)
    
    if event == '	' and len(sym):
        ui_handle.update(sym[0])
    elif event == "-DOWNKEY-" or (len(sym) and sym[0] == new_text) or not len(sym) or new_text == '':
        return
    else:
        show_combo_tooltip(ui_handle=ui_handle, tooltip=sym, space_ref=space_ref, text_len=text_len)

autocomp_el_keys = ['-AIN-', '-FEATURECOMBO-']
autocomp_options = {}
def refresh_autocomp_options():
    global autocomp_options
    autocomp_options = {'-AIN-': {'values': choices, 'show_on_empty': False}, 
                        '-FEATURECOMBO-': {'values': orga_selection, 'show_on_empty': True}}
refresh_autocomp_options()
active_element = win[[i for i in win.AllKeysDict.keys()][0]]
active_element.set_focus()  
space_ref = win['-SPACEREF-']
text_len = win['-TEXTLEN-']
text_len.update(text_color=text_len.BackgroundColor)
sg.PySimpleGUI.TOOLTIP_BACKGROUND_COLOR = win['-AIN-'].BackgroundColor
sg.set_options(tooltip_font=(('Helvetica', font_size)))
win.refresh()


# call initials on first start, changing initals later is not allowed because it might create a mess when updating plasmids on ice as a new folder would be created
initials_value = db['Settings']['initials']
if initials_value == '__':
    initials_set = sg.popup_get_text('Please enter your initials. This name will be used as folder name when uploading plasmids to ice.\nPlease note that you cannot change the name anymore at a later time.')
    win['Settings.initials'].update(initials_set)
    db['Settings'].save_record(display_message=False)


# WHILE
#-------------------------------------------------------
if autosync == 1:
    sync_gsheets()
    choices = autocomp()
    orga_selection = select_orga()
    win['-FEATURECOMBO-'].Update(values = orga_selection)
    win['-SETSELORGA-'].Update(values = orga_selection)
    refresh_autocomp_options()
check_plasmids()
check_features()
check_organisms()

while True:
    event, values = win.read()
    print('event:', event)
    for key in autocomp_el_keys:
        clear_combo_tooltip(ui_handle=win[key])
    #print('values:', values)

    if event == 'featureActions.db_save':
        old_annotation = db['Features']['annotation'] or ''

### Let PySimpleSQL process its own events! Simple! ### 
    if  db.process_events(event, values):
        logger.info(f'PySimpleDB event handler handled the event {event}!')
        
### Fix display ###
    if event == 'cassettesActions.table_insert':
        db['Plasmids'].save_record(display_message=False)
        selected_plasmid=db['Plasmids']['id']
        db['Plasmids'].set_by_pk(selected_plasmid)
    elif event == 'cassettesActions.db_save':
        check_features()
        check_organisms()
    elif event == 'featureActions.db_save':
        corrected_value = db['Features']['annotation']
        corrected_value = corrected_value.replace('-', '_')
        corrected_value = corrected_value.replace('[', '(')
        corrected_value = corrected_value.replace(']', ')')
        corrected_value = corrected_value.replace(' ', '_')
        win['Features.annotation'].update(corrected_value)
        db['Features'].save_record(display_message=False)
        choices = autocomp()
        if choices.count(corrected_value) > 1:
            sg.popup('There already exists a feature with the same annotation: ' + corrected_value + '.\n The entry is invalid, please enter a new annotation name!')
            win['Features.annotation'].update('')
            db['Features'].save_record(display_message=False)
            choices = autocomp()
        elif db['Settings']['autosync'] == 1:
            sync_gsheets()
            choices = autocomp()
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        if old_annotation and old_annotation != corrected_value:
            update_cassettes({old_annotation:corrected_value})
            update_alias({old_annotation:corrected_value})
        refresh_autocomp_options()
        check_features()
        check_organisms()
        
    elif event == 'settingsActions.db_save':
        db['Settings'].save_record(display_message=False)
        user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync = read_settings()
        sg.user_settings_set_entry('-THEME-', (values['Settings.style']))
        sg.user_settings_set_entry('-SCALE-', (values['Settings.scale']))
        sg.user_settings_set_entry('-FONTSIZE-', (values['Settings.font_size']))
        win['Settings.style'].update(disabled=True) # not a perfect solution
        win['Settings.style'].update(value=values['-SETSTYLE-']) 
        win['Settings.initials'].update(disabled=True)
    elif event == 'Settings.ice.quick_edit':
        db['Settings'].save_record(display_message=False) 
    elif event in ['settingsActions.edit_protect', 'featureActions.edit_protect', 'plasmidActions.edit_protect']:
        # enable extra elements
        extra_el_disabled = not extra_el_disabled
        win['-DUPLICATE-'].update(disabled=extra_el_disabled)
        win['-THISICE-'].update(disabled=extra_el_disabled)
        win['-ADDFEATURE-'].update(disabled=extra_el_disabled)
        win['-ALIAS_IN-'].update(disabled=extra_el_disabled)
        win['insGb'].update(disabled=extra_el_disabled)
        win['insElement'].update(disabled=extra_el_disabled)
        win['-down_att-'].update(disabled=extra_el_disabled)
        win['-down_gb-'].update(disabled=extra_el_disabled)
        win['-ADDORGA-'].update(disabled=extra_el_disabled)
        win['-DESTROYORGA-'].update(disabled=extra_el_disabled)
        win['-APPROVAL-'].update(disabled=extra_el_disabled)
        win['-ADDFAV-'].update(disabled=extra_el_disabled)
        win['-AIN-'].update(disabled=extra_el_disabled)
        win['-VARIANT-'].update(disabled=extra_el_disabled)
        win['-FEATURECOMBO-'].update(disabled=extra_el_disabled)
        #win['Features.organism'].update(disabled=True) #always disabled, not working?
        win['Settings.name'].update(disabled=extra_el_disabled)
        win['Settings.initials'].update(disabled=True)
        win['Settings.email'].update(disabled=extra_el_disabled)
        win['Settings.institution'].update(disabled=extra_el_disabled)
        win['Settings.ice'].update(disabled=extra_el_disabled)
        win['Settings.gdrive_glossary'].update(disabled=extra_el_disabled)
        win['Settings.gdrive_id'].update(disabled=extra_el_disabled)
        win['Settings.style'].update(disabled=extra_el_disabled)
        win['-SETSTYLE-'].update(disabled=extra_el_disabled)
        win['Settings.scale'].update(disabled=True) 
        win['Settings.font_size'].update(disabled=True) 
        win['Settings.horizontal_layout'].update(disabled=extra_el_disabled)
        win['Settings.duplicate_gmos'].update(disabled=extra_el_disabled)
        #win['Settings.upload_completed'].update(disabled=extra_el_disabled) # disabled for now
        #win['Settings.upload_abi'].update(disabled=True) # disabled for now
        win['Settings.use_ice'].update(disabled=extra_el_disabled)
        if sys.platform != "win32":
            win['Settings.use_filebrowser'].update(disabled=extra_el_disabled)
        win['Settings.use_gdrive'].update(disabled=extra_el_disabled)
        win['Settings.zip_files'].update(disabled=extra_el_disabled)
        win['Settings.autosync'].update(disabled=extra_el_disabled)
        win['-SETSELORGA-'].update(disabled=extra_el_disabled)
        win['-ADDSELORGA-'].update(disabled=extra_el_disabled)
        win['-COPYFAVORGA-'].update(disabled=extra_el_disabled)

        # protect synced entries (Features, Organisms)
        feature_protection = db['Features']['synced']
        organism_protection = db['Organisms']['synced']
        if feature_protection == 1:
            win['Features.annotation'].update(disabled=True)
            win['Features.alias'].update(disabled=True)
            win['Features.risk'].update(disabled=True)
            win['Features.organism'].update(disabled=True)
            win['-FEATURECOMBO-'].update(disabled=True)
        if organism_protection == 1:
            win['Organisms.full_name'].update(disabled=True)
            win['Organisms.short_name'].update(disabled=True)
            win['Organisms.RG'].update(disabled=True)

    elif event == 'plasmidActions.table_insert':
        selected_plasmid=db['Plasmids']['id']
        newname = 'p' + initials + '000'
        newname_input = sg.popup_get_text('Enter the name for the new plasmid', default_text=newname)
        win['Plasmids.name'].update(newname_input)
        db['Plasmids'].save_record(display_message=False)
        db['Plasmids'].set_by_pk(selected_plasmid)

    elif event == 'featureActions.table_delete':
        choices = autocomp()
        refresh_autocomp_options()

    elif event == 'organismActions.table_delete':
        orga_selection = select_orga()
        refresh_autocomp_options()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)

    elif event == 'organismActions.db_save':
        orga_selection = select_orga()
        refresh_autocomp_options()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)
        if orga_selection.count(db['Organisms']['short_name']) > 1:
            sg.popup('There already exists an organism with the same short name: ' + db['Organisms']['short_name'] + '.\n The entry is invalid, please enter a new annotation name!')
            win['Organisms.short_name'].update('')
            db['Organisms'].save_record(display_message=False)
            choices = autocomp()
        elif db['Settings']['autosync'] == 1:
            sync_gsheets()
            choices = autocomp()
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        refresh_autocomp_options()
        check_organisms()

### Duplicate plasmid ###
    elif event == '-DUPLICATE-':
        duplicate_plasmid = sg.popup_yes_no('Do you wish to duplicate the plasmid entry?')
        if duplicate_plasmid == 'Yes':
            user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync = read_settings()
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
        upload = sg.popup_yes_no('Updating plasmid {} on servers. Proceed?'.format(thisice))
        if upload == 'Yes':
            if use_ice == 1:
                upload_ice(thisice, use_ice=use_ice)
            if use_filebrowser == 1 or use_gdrive == 1:
                upload_file_servers(thisfile=thisice, use_filebrowser=use_filebrowser, use_gdrive=use_gdrive, zip_files=zip_files)

    elif event == '-ADDORGA-':
        try:
            db['Plasmids'].save_record(display_message=False)
            selected_plasmid = db['Plasmids']['id']
            organism_index = db['Plasmids']['organism_selector']
            add_organism(organism_index)

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
                        add_organism(orga_id)
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
        db['Plasmids'].save_record(display_message=False)
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
            download_path = user_data
            name_file = db['Plasmids']['gb_name']
            if name_file != '':
                file= open(os.sep.join([download_path, name_file]), 'r+')
        except FileNotFoundError:
            if name_file != '':
                file= open(os.sep.join([download_path, name_file]), 'w+')
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
            readBlobData(att_id, att_name, user_data)
        except Exception as e:
            sg.popup(e)

### autocomplete ###
    # pressing down arrow will trigger event -AIN- then aftewards event Down:
    elif event == '-LEFTCLICK-': 
        try:
            clear_combo_tooltip(ui_handle=active_element)
        except:
            pass
        try:
            active_element = win.FindElementWithFocus() 
            if active_element.key in ['cassettesSelector', 'gmoSelector', 'attachmentSelector', 'organismselectionSelector', 'favouritesSelector']:
                win.write_event_value(active_element.key, values[active_element.key])
                active_element.block_focus()
        except:
            pass
    elif event == '-ENTERKEY-':
        clear_combo_tooltip(ui_handle=active_element)
    elif event == '	' or event == '-DOWNKEY-':
        if active_element.key in autocomp_el_keys:
            autocomplete(event, values, auto_options=autocomp_options[active_element.key], ui_handle=active_element, space_ref=space_ref, text_len=text_len)
    elif event == '-DROPDOWN-':
        if active_element.key in autocomp_el_keys:
            print("hj")
            win[values['-DROPDOWN-']].Widget.event_generate('<Down>')
    elif event == '-ADDFEATURE-':
        selected_feature = values['-AIN-']
        if selected_feature[2:-3] in choices: # the truncation of values['-AIN-'][2:-3] is a hack to deal with the shape of 'choices' such as: ('Feature1'),
            selected_feature = selected_feature[2:-3]
        if selected_feature == "":
            pass
        else:
            variant = '['+values['-VARIANT-']+']'
            if db['Cassettes']['content'] == 'Empty' or db['Cassettes']['content'] == '':
                if values['-VARIANT-'] != '':
                    win['Cassettes.content'].update(selected_feature + variant)
                else:
                    win['Cassettes.content'].update(selected_feature)
            elif values['-VARIANT-'] != '':
                win['Cassettes.content'].update(db['Cassettes']['content'] + '-' + selected_feature + variant)
            else:
                win['Cassettes.content'].update(db['Cassettes']['content'] + '-' + selected_feature)
            db['Cassettes'].save_record(display_message=False)
            win['-AIN-'].update('')
            win['-VARIANT-'].update('')
            check_features()
            check_organisms()
            
    elif event == '-ALLEXCEL-':
        connection = sqlite3.connect(database)
        pd.read_sql_query('SELECT * FROM Features', connection).to_excel(os.sep.join([user_data, 'ALL_nucleic_acid_features.xlsx']), index=False, engine='xlsxwriter')
        connection.close()
        sg.popup('Done.')
    elif event == '-ALLEXCELORGA-':
        connection = sqlite3.connect(database)
        pd.read_sql_query('SELECT * FROM Organisms', connection).to_excel(os.sep.join([user_data, 'ALL_organisms.xlsx']), index=False, engine='xlsxwriter')
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
            target = os.sep.join([user_data, 'USED_nucleic_acid_features' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'])
            writer = pd.ExcelWriter(target, engine='xlsxwriter')
            # also drop id column here:
            pd.read_sql_query('SELECT annotation, alias, risk, organism, uid FROM Features WHERE annotation IN {}'.format(str(tuple(lst))), connection).to_excel(writer, sheet_name='Sheet1', index=False, startrow=0)
            connection.close()

            workbook  = writer.book
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
            format = workbook.add_format({'text_wrap': True, 'border': 1})
            worksheet = writer.sheets['Sheet1']

            worksheet.write(0, 0, 'Annotation', header_format)
            worksheet.write(0, 1, 'Alias', header_format)
            worksheet.write(0, 2, 'Risk', header_format)
            worksheet.write(0, 3, 'Organism', header_format)
            worksheet.write(0, 4, 'UID', header_format)

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
            worksheet.set_column(4, 3, 34, format)

            writer.close()

            sg.popup('Done.')
        except:
            sg.popup('There must be more than one element in the list and used in Cassettes in order to use the export function.')
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
            target = os.sep.join([user_data, 'USED_organisms' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'])
            writer = pd.ExcelWriter(target, engine='xlsxwriter')

            pd.read_sql_query('SELECT full_name, short_name, RG, uid FROM Organisms WHERE short_name IN {}'.format(str(tuple(lst5))), connection).to_excel(writer, sheet_name='Sheet1', index=False, startrow=0)
            cursor.close()
            connection.close()

            workbook  = writer.book
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center', 'border': 1, 'bg_color': '#D3D3D3'})
            format = workbook.add_format({'text_wrap': True, 'border': 1})
            worksheet = writer.sheets['Sheet1']

            worksheet.write(0, 0, 'Full name', header_format)
            worksheet.write(0, 1, 'Short name', header_format)
            worksheet.write(0, 2, 'Risk group', header_format)
            worksheet.write(0, 3, 'UID', header_format)

            footer = initials +' List of used organisms'
            worksheet.set_footer(footer)
            worksheet.set_portrait()
            worksheet.repeat_rows(0)
            worksheet.set_paper(9)
            worksheet.fit_to_pages(1, 0)  # 1 page wide and as long as necessary.

            worksheet.set_column(0, 0, 50, format)
            worksheet.set_column(1, 1, 20, format)
            worksheet.set_column(2, 2, 10, format)
            worksheet.set_column(3, 2, 34, format)

            writer.close()

            sg.popup('Done.')

        except:
            sg.popup('There must be more than one element in the list in order to use the export function.')

    elif event == '-ADDFEATURESEXCEL-':
        excel_feature_file_path = sg.popup_get_file('Select the template *.xlsx file containing feature definitions to import.\nWe will only add new entries which not exist yet with the same name.')
        if excel_feature_file_path == '' or excel_feature_file_path == None:
            pass
        else:
            filename = os.path.basename(excel_feature_file_path)
            if filename == '':
                sg.popup('Select a file.')
            else:
                try:
                    wb = pd.read_excel(excel_feature_file_path, sheet_name = 0)
                    add_to_features(wb)
                    choices = autocomp()
                except FileNotFoundError:
                    sg.popup("File " + excel_feature_file_path + " does not exist.")

    elif event == '-ADDGOOGLE-': #to be removed
        try:
            #import ssl # import not here
            ssl._create_default_https_context = ssl._create_unverified_context #monkeypatch
            sheet_id = db['Settings']['gdrive_glossary']
            sheet_name = 'features'
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            wb = pd.read_csv(url)
            add_to_features(wb)
            choices = autocomp()
            refresh_autocomp_options()
        except Exception as e:
            sg.popup(e)

    elif event == '-ADDEXCELORGA-': 
        file = sg.popup_get_file("Select file")
        if file:
            try:
                wb = pd.read_excel(file, sheet_name = 0)
                add_to_organisms(wb)
                orga_selection = select_orga()
                refresh_autocomp_options()
                win['-FEATURECOMBO-'].Update(values = orga_selection)
                win['-SETSELORGA-'].Update(values = orga_selection)
            except FileNotFoundError:
                sg.popup("File " + file + " does not exist. You might have to rename it.")
            except Exception as e:
                sg.popup(e)

    elif event == '-FEATURESYNC-' or event == '-ORGASYNC-':
        try:
            sync_gsheets()
            choices = autocomp()
            orga_selection = select_orga()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
            refresh_autocomp_options()

        except Exception as e:
            sg.popup(e)

    elif event == '-ADDGOOGLEORGA-':
        try:
            sheet_id = db['Settings']['gdrive_glossary']
            sheet_name = 'organisms'
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            wb = pd.read_csv(url)
            add_to_organisms(wb)
            choices = autocomp()
            orga_selection = select_orga()
            refresh_autocomp_options()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['-SETSELORGA-'].Update(values = orga_selection)
        except Exception as e:
            sg.popup(e)

    elif event == '-FEATUREINFO-':
        sg.popup('Dashes and brackets "-, [, ]" in annotation names are not allowed and will be replaces by underscores and parentheses "_, (, )".')
    elif event == '-FEATURECOMBO-':
            orga_selection = select_orga()
            refresh_autocomp_options()
            win['-FEATURECOMBO-'].Update(values = orga_selection)
            win['Features.organism'].update(disabled=True) # not a perfect solution
            win['Features.organism'].update(value=values['-FEATURECOMBO-'])
    elif event == '-ADDSELORGA-':
            orga_selection = select_orga()
            refresh_autocomp_options()
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

### Upload to ICE, Filebrowser, GDrive ###
    elif event == '-SERVERS-':
        configured_services = []
        if use_ice == 1:
            configured_services.append('JBEI/ice')
        if use_gdrive == 1:
            configured_services.append('GDrive')
        if use_filebrowser == 1:
            configured_services.append('Filebrowser')
        if len(configured_services) == 0:
            configured_services = ['NONE']
        upload = sg.popup_yes_no('Depending on database size and network, the upload may take some time. Currently enabled data upload servers: "{}". In any case, data will be exported locally. Proceed?'.format(" and ".join(configured_services)))
        if upload == 'Yes':
            upload_ice(thisice='', use_ice=use_ice)
            upload_file_servers(thisfile='', use_filebrowser=use_filebrowser, use_gdrive=use_gdrive, zip_files=zip_files)

### Formblatt Z ###
    elif event == '-FORMBLATT-':
        features_check = check_features()
        organisms_check = check_organisms()
        if features_check[0] == True and organisms_check[0] == True:
            event, values = sg.Window('Choose', [[sg.T('Choose a language')],[sg.LBox(['de','en'],size=(10,3))],[sg.OK()]]).read(close=True)
            if len(values[0]) > 0:
                lang = values[0][0]
            else:
                lang = 'de'
            formblatt = generate_formblatt(lang)
            today = date.today()
            target = os.sep.join([user_data, 'Formblatt-Z' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'])
            
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
        target = os.sep.join([user_data, 'Plasmidlist' + '_' + user_name + '_' + str(today.strftime("%Y-%m-%d")) + '.xlsx'])
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
        refresh_autocomp_options()
        win['-FEATURECOMBO-'].Update(values = orga_selection)
        win['-SETSELORGA-'].Update(values = orga_selection)

### Info in settings ###
    elif event == '-SETTINGSINFO-':
        sg.popup(appname + ' ' + str(version_no) + ', ' + vdate)

    elif event == '-CTRL-E-':
        win['Settings.scale'].update(disabled=False)
        win['Settings.font_size'].update(disabled=False)

### Exit ###
    elif event == sg.WIN_CLOSED or event == 'Exit':
        user_name, initials, email, institution, ice, duplicate_gmos, upload_completed, upload_abi, scale, font_size, style, ice_instance, ice_token, ice_token_client, horizontal_layout, filebrowser_instance, filebrowser_user, filebrowser_pwd, use_ice, use_filebrowser, use_gdrive, zip_files, autosync = read_settings()
        sg.user_settings_set_entry('-THEME-', style)
        sg.user_settings_set_entry('-SCALE-', float(scale))
        sg.user_settings_set_entry('-FONTSIZE-', int(font_size))
        sg.user_settings_set_entry('-HORIZONTAL-', int(horizontal_layout))
        db=None              # <= ensures proper closing of the sqlite database and runs a database optimization
        break
    else:
        active_element = win.FindElementWithFocus()
        if active_element and active_element.key in autocomp_el_keys:
            autocomplete(event, values, auto_options=autocomp_options[active_element.key], ui_handle=active_element, space_ref=space_ref, text_len=text_len)
            # protect editing already synced Features, Organisms
        feature_protection = db['Features']['synced']
        organism_protection = db['Organisms']['synced']
        if feature_protection == 1:
            win['Features.annotation'].update(disabled=True)
            win['Features.alias'].update(disabled=True)
            win['Features.risk'].update(disabled=True)
            win['Features.organism'].update(disabled=True)
        if organism_protection == 1:
            win['Organisms.full_name'].update(disabled=True)
            win['Organisms.short_name'].update(disabled=True)
            win['Organisms.RG'].update(disabled=True)