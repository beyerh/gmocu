# GMOCU

User-oriented plasmid database with GMO documentation in accordance with the German GenTAufzV regulation (*Formblatt-Z*).

<img src="./img/navigation.gif" width=30% height=30%>

## Installation

### Download

Download executable GMOCU packages for macOS, Windows, and Linux from the [Releases](https://github.com/beyerh/gmocu/releases) page. See [video tutorial](#software-installation).

Alternatively, you may execute the ```gmocu.py``` script file containing the source code (requires installation of dependencies).

For instructions on installing a local instance of JBEI/ice (optional), see further below.

### Upgrade versions

Download the new [Release]([Releases · beyerh/gmocu · GitHub](https://github.com/beyerh/gmocu/releases)) and replace the previous version with it. GMOCU will resource the date form the GMOCU folder in the user directory and eventually update the database file structure. [Backup](#backup) your data before updating.

## Usage

### Video tutorials

<details>
  <summary>Software download and installation</summary>
  <a name="software-installation"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/b80ad6e4-4eae-463d-b651-d45ecbe82d23.mp4' />
</details>

<details>
  <summary>Getting started and importing a glossary</summary>
  <a name="getting-started"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/b0057bca-9b67-4771-bcc1-b4d5871266bd.mp4' />
</details>

<details>
  <summary>Data import from another GMOCU instance</summary>
  <a name="data-import"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/9a4d021a-7b93-4ed8-8109-c224b9d83e65.mp4' />
</details>

<details>
  <summary>Data entry</summary>
  <a name="data-entry"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/ffd65faf-d73d-4b53-9378-3890d2d044a9.mp4' />
</details>

<details>
  <summary>Configure JBEI/ice and upload part entries</summary>
  <a name="jbei-ice"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/e547da3b-d598-4b9e-9677-4a8074cc3feb.mp4' />
</details>

<details>
  <summary>Generating reports and retrieving attachments</summary>
  <a name="reports"></a>
  <video src='https://github.com/beyerh/gmocu/assets/116307465/e5b35398-446f-4a21-b0af-7332ecc5a837.mp4' />
</details>

### Settings

| Setting            | Description                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initials           | Define the user or project initials. Based on the entry, a folder on JBEI/ice will be generated into which plasmid entries will be uploaded. The initials should not and cannot be changed anymore at a later date.                                                                                                                                                                |
| GMO institute      | Provides governmental information on the GMO facility (Az. and Anlage Nr.) which will appear on the Formblatt-Z.                                                                                                                                                                                                                                                                   |
| Server credentials | Generate an API key for a shared JBEI/ice account hosted locally or on the public server. Enter the key. Several accounts can be added to push plasmid data into multiple accounts if desired. See the [video tutorial](#getting-started). Enter Filebrowser address and user/password information.                                                                                |
| Google Sheet ID    | Google Sheet ID: Upload the glossary file ```GDrive_glossary.xlsx``` to a Google Drive account and make it public. Extract the identifier code from the link and enter. You can also test with this provided example link: ```https://docs.google.com/spreadsheets/d/1QnyWcntaYdYkEqyUStWZedsb4ZKLsd18/edit#gid=1994557483```, Identifier: ```1QnyWcntaYdYkEqyUStWZedsb4ZKLsd18``` |
| Style              | Visual theme.                                                                                                                                                                                                                                                                                                                                                                      |
| Horizontal layout  | Layout option for small or low resolution screens.                                                                                                                                                                                                                                                                                                                                 |
| Duplicate GMOs     | When duplicating a selected plasmid, GMOs will also be copied, however, with the current date. (Default, false).                                                                                                                                                                                                                                                                   |
| Upload completed   | Only upload plasmid entries that were set to the status "Complete". (Default, false).                                                                                                                                                                                                                                                                                              |
| Use JBEI/ice       | Enable uploading to the JBEI/ice instance defined in "Server credentials".                                                                                                                                                                                                                                                                                                         |
| Use Filebrowser    | Enable uploading to the Filebrowser instance defined in "Server credentials".                                                                                                                                                                                                                                                                                                      |
| Target organisms   | Define target organisms (working organisms for GMO generation). The organisms must first be present in the organism glossary.                                                                                                                                                                                                                                                      |
| Fav. organisms     | Select some of the target organisms for generating several GMOs with one click using the ':)' convenience function. All organisms in ```Fav. organisms``` must be present in ```Target organisms```!                                                                                                                                                                               |

### Where is all data stored?

All files written by GMOCU (including various exports and the ```gmocu.db``` SQLite database file) are located in the [GMOCU user data folder](#where-is-all-data-stored), residing in your home directory. Depending on the operating system, the location is:

macOS:
`/Users/<user>/GMOCU`

Windows:
`C:\Users\<user>\GMOCU`

Linux:
`/home/<user>/GMOCU`

### Glossaries

The ```Nucleic acids``` and ```Organisms``` glossaries can be imported and exported from and to ```*.xlsx``` files in the respective tabs. Another convenient and recommended way to manage the glossaries is to upload the ```GDrive_glossary.xlsx``` file to a [Google Drive](https://www.google.com/drive/) account, make the access public (Share --> Anyone with the link --> Set access rights to 'Editor' or 'Viewer'), and set the Google Sheets ID in the Settings tab (see section Settings). Entries can now be imported using the button ```Add entries from Google Sheets which not yet exist```. This approach allows a convenient collection of `Nucleic acid` and `Organism` definitions in teams. Please do not modify the names of headers and sheets. See the [video tutorial](#getting_started).

### Plasmid data

Enter plasmid data and GMOs in the ```Plasmid data``` tab. There are also functions for uploading Genebank plasmid maps and associated data. The plasmid maps will be added to JBEI/ice on upload. There are several convenient functions for adding GMO-relevant cassettes and GMO entries. Please import or enter ```Nucleic acids``` and ```Organisms``` glossaries and fill in all ```Settings``` before starting to add plasmid data. See [video tutorial](#data_entry).

### Example data

The ```example``` folder provides a selected set of `Nucleic acid` and `Organism` definitions (`GDrive_glossary.xlsx`) which can serve as a starting point for developing an inventory. The file can be uploaded to Google Drive for collaborative editing and import (see [Glossaries](#glossaries)). Similar lists are enclosed in the ``templates`` folder of the [GMOCU user data folder](#where-is-all-data-stored).

The `example` folder further provides a ```gmocu.db``` file with testing data. The file can be copied into the [GMOCU user data folder](#where-is-all-data-stored). If no ```gmocu.db``` file exists, GMOCU will generate an empty database file on the initial start.

### GMO and Maintainance

#### Maintenance

Check for completeness of the glossaries and duplicates of plasmid entries.

#### JBEI/ice

Upload plasmid entries to JBEI/ice if configured in the Settings. Each upload will overwrite the information on the server. When ```Only new plasmids``` is checked, GMOCU will only upload entries with plasmid names that do not yet exist in the respective folder on the ICE server. Another way to update the information of a single plasmid, e.g. after editing is by pressing the ```ICE``` button in the top right corner of the ```Plasmid data``` tab. See the [video tutorial](#jbei-ice).

#### Filebrowser

Upload plasmid genebank files and any files attached as "Attachement" together with a text file containing plasmid data in a folder tree to a local Filebrowser server (see below for configuration).

#### GMO

Generate a simple ```Plasmid list``` or the ```Formblatt Z``` biosafety report required for governmental regulations. Also, export the ```Nucleic acids``` and ```Organisms``` in the respective tabs. The files will appear in the [GMOCU user data folder](#where-is-all-data-stored).

#### Data import

Import data from another ```gmocu.db``` file together with the associated nuclei acid features and organisms if they are not yet present in the glossary of the app. This function is useful for combining data from several users into one database file. See the [video tutorial](#data-import).

### Backup

To backup the database it suffices to copy the ```gmocu.db``` SQLite database file located in the [GMOCU user data directory](#where-is-all-data-stored). The file contains all relevant data. Alternatively you may backup the entire GMOCU folder. It is possible to store the ```gmocu.db``` file at a location which is synced via a cloud service such as Dropbox. Then, replace the file in the application folder with a soft link to that file. That way, one can work with the same database from different computers. Regular backups are recommended.

### Manual data editing

The data stored in tables within the `gmocu.db` file can be accessed by software such as [DB Browser for SQLite](https://sqlitebrowser.org/). While we generally recommend refraining from manual editing, it might be required in particular cases.

### Link to the public registry JBEI/ice database

Make a free account at the [JBEI public registry](https://public-registry.jbei.org/). Generate an access token in the account settings and add it in the GMOCU settings tab. Note that you may not be able to delete entries again from the registry. Alternatively, install a local JBEI/ice instance (recommended, [see below](#install-jbeiice-as-docker-container-locally-or-on-a-server)).

### Hidden settings

### Specify scaling and font size and reset OS-dependent detection

In the Settings tab, the fields for defining font size and scaling are inactivated (grayed out). Enable them by pressing the key combination ```Ctrl + e```. Now you can specify the values and save. Restart GMOCU.

In order to reset the OS-dependent automated setting of the font size and scaling values, enter ```__``` (double underscore) into the fields and save. Close GMOCU and delete the file ```gmocu.json``` in the project directory. Restart GMOCU.

## Install JBEI/ice as docker container locally or on a server

- For reference, see [the official description](https://github.com/JBEI/ice/tree/trunk/docker).

- Install Docker Desktop, and set startup after login in settings.

- Set static IP in Network Settings and change the computer name for network access via ```name.local```.

- Clone repo:
  
  ```bash
  git clone https://github.com/beyerh/gmocu.git
  ```

- Copy modified docker-compose.yml containing PASSWORD fix and autostart:
  
  ```bash
  mkdir ice
  cp gmocu/docker-compose.yml ice/
  cd ice
  ```

- Either enter the static IP address set above into the docker-compose.yml file:
  
  ```yaml
  134.99.70.14:9999:8080
  ```
  
  or leave the address as localhost for installation on a local machine without network access:
  
  ```yaml
  127.0.0.1:9999:8080
  ```

- Install JBEI/ice from the docker hub, create containers, and launch:
  
  ```bash
  docker pull jbei/ice
  docker-compose up
  ```

- Call the address set above in a browser and log in with "Administrator" as user and password.

- Create a new user account and setup the access token to use in the GMOCU settings.

### Install Filebrowser on server

For uploading files including attachments, a [Filebrowser](https://filebrowser.org/) server can be used (e.g. on the same computer running the jBEI/ice server). The installation is very simple (see homepage for instructions for Windows):

```
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash
```

Initiate the Filebrowser instance with:

```bash
filebrowser config init -r /path/to/folder/on/server -a 134.99.70.14


```

Replace the IP address with the static IP of your server or skip ``` -a ip-address``` if you would like to run the server on localhost. Start on boot with ```filebrowser```.

### Possible backup solution for JBEI/ice docker volumes

Install [docker-vackup](https://github.com/BretFisher/docker-vackup).

Script the following commands and execute them e.g. daily. Include the tarballs into your regular backup solution:

```bash
cd ~/ &&
/usr/local/bin/vackup export ice_ice_home ice_ice_home.tar.gz &&
/usr/local/bin/vackup export ice_ice_index ice_ice_index.tar.gz &&
/usr/local/bin/vackup export ice_postgres_db ice_postgres_db.tar.gz
```

You may execute the the backup commands via an automator app on macOS (this requires including the `PATH` variable in the script `PATH=$PATH:/usr/local/bin`) and schedule with the calendar app. Alternatively a corn job executed as user might work. Other backup strategies are possible.

## Development

### Anaconda development environment and deployment of executables

With [Anaconda](https://www.anaconda.com/) installed, add the conda-forge repository:

```python
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Set up the developmental ```gmocu``` environment:

```python
conda create --name gmocu python=3.9
conda activate gmocu

conda install PySimpleGUI pandas Pillow xlsxwriter openpyxl python-levenshtein
pip install icebreaker pyinstaller==5.13.2 filebrowser-client
```

Deploy executable using Pyinstaller:

```python
conda activate gmocu
pyinstaller gmocu.spec
```

The version numbers of the environment packages used for the deployment of GMOCU-0.4 are listed in the file ```GMOCU-0.4_env_packages.txt```.

### Modifying the information content of the generated reports

Customized reports can be generated by modifying the respective functions in the ```gmocu.py``` file. Data can be sourced from the various tables and fields stored in the SQLite file ```gmocu.db```. For an overview, see the content of the file ```gmocu.sql```.

For biosafety reports, the relevant function to modify is called ```generate_formblatt(lang)```. Here, under the section ```#pack data```, the content can be defined which subsequently has to be inserted into the pandas data frame at the end of the function.

Plasmid lists can be modified within the function ```generate_plasmidlist()```, following the same concept as with biosafety reports.

Formatting parameters such as column widths of the generated output ```*.xslx``` file can be defined in the ```while``` loop where the functions are called.

## Resources

- [Wagner C, Urquiza-Garcia U, Zurbriggen MD, Beyer HM. GMOCU: Digital Documentation, Management, and Biological Risk Assessment of Genetic Parts. Adv Biol (Weinh). 2024 Jan 23:e2300529.](https://pubmed.ncbi.nlm.nih.gov/38263723/)
- [PySimpleSQL](https://github.com/PySimpleSQL)
- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [ICEbreaker](https://edinburgh-genome-foundry.github.io/icebreaker/)
- [Filebrowser-client](https://github.com/chermed/filebrowser-client)
