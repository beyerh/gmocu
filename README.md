# GMOCU

User-oriented plasmid database with GMO documentation in accordance with the Germany GenTAufzV regulation (*Formblatt-Z*).

<img src="./img/navigation.gif" width=30% height=30%>

## Installation

### Download

Download executale GMOCU packages for macOS, Windows, and Linux from the [Releases](https://github.com/beyerh/gmocu/releases) page.

Alternatively you may execute the gmocu.py script file (recuires intallation of dependencies).

For instructions on installing a local instance of jbei/ICE (optional), see further below.

## Usage

### Video tutorials

#### Getting started and importing a glossary

#### Data import from another GMOCU instance

#### Data entry

#### Configure jbei/ICE and upload part entries

#### Generating reports and attachment retrieval



### Settings

| Setting          | Description                                                                                                                                                                                                                                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initials         | Define the user or project initials. Based on the entry, a folder on jbei/ICE will be generated into which plasmid entries will be uploaded. The initials should not and cannot be changed anymore at a later date.                                                                                                                                      |
| GMO institute    | Provide governmental information on the GMO facility (Az. and Anlage Nr.) which will appear on the Formblatt-Z.                                                                                                                                                                                                                                          |
| jbei/ICE API     | Generate an API key for a shared jbei/ICE account either hosted locally or on the public server. Enter the key. Several accounts can be added in order to push plasmid data into multiple accounts if desired. See the [video tutorial](####configure-jbei/ICE-and-upload-part-entries).                                                                                                                                           |
| Google Sheet ID  | Google Sheet ID: Upload the glossary file ```GDrive_glossary.xlsx``` to a Google Drive account and make it public. Extract the identifier code from the link and enter. You can also test with this provided example link: ```https://docs.google.com/spreadsheets/d/1QnyWcntaYdYkEqyUStWZedsb4ZKLsd18/edit#gid=1994557483```, Identifier: ```1QnyWcntaYdYkEqyUStWZedsb4ZKLsd18``` |
| Style            | Visual theme.                                                                                                                                                                                                                                                                                                                                            |
| Duplicate GMOs   | When duplicating a selected plasmid, GMOs will also be copied, however, with the current date. (Default, false)                                                                                                                                                                                                                                          |
| Upload completed | Only upload plasmid entries that were set to the status "Complete". (Default, false)                                                                                                                                                                                                                                                                     |
| Target organisms | Define target organisms (working organisms for GMO generation). The organisms must first be present in the organism glossary.                                                                                                                                                                                                                            |
| Fav. organisms   | Select some of the target organisms for generating several GMOs with one click using the ':)' convenience function. All organisms in ```Fav. organisms``` must be present in ```Target organisms```!                                                                                                                                                     |

### Glossaries

The ```Nucleic acids``` and ```Organisms``` glossaries can be imported and exported from and to ```*.xlsx``` files in the respective tabs. Another convenient and recommended way to manage the glossaries is to uplad the the ```GDrive_glossary.xlsx``` file to an Google Drive account (https://www.google.com/drive/), make the access public (Share --> Anyone with the link --> Set access rights to 'Editor' or 'Viewer'), and set the Google Sheets ID in the Settings tab (see section Settings). Entries can now be imported using the button ```Add entries from Google Sheet which not yet exist```. This approach allows a convinient collection of `Nuclaic acid` and `Organism` definitions in teams. Please do not modify the names of headers and sheets. See the video tutorial [video tutorial](####getting-started-and-importing-a-glossary).

### Plasmid data

Enter plasmid data and GMOs in the ```Plasmid data``` tab. There are also functions for uploading Genebank plasmid maps and associated data. The plasmid maps will be added to jbei/ICE on upload. There are several convenience functions for adding GMO-relevant Cassettes and GMO entries. Please import or enter ```Nucleic acids``` and ```Organisms``` glossaries and fill in all ```Settings``` before starting to add plasmid data. See [video tutorial](########data-entry).

### GMO and Maintainance

#### Maintenance

Check for completness of the glossaries and for duplicates of plasmid entries.

#### jbei/ICE

Upload plasmid entries to jbei/ICE. Each upload will overwrite the information on the server. When ```Only new plasmids``` is checked, GMOCU will only upload entries with plasmid names which do not yet exist in the respective folder on the ICE server. Another way to update the information of a single plasmid, e.g. after edit is by pressing the ```ICE``` button on the top right corner in the ```Plasmid data``` tab. See the [video tutorial](####configure-jbei/ICE-and-upload-part-entries).

#### GMO

Generate a simple ```plasmid list``` or the ```Formblat Z``` required for the governmental regulations. Also export the ```Nucleic acids``` and ```Organisms``` in the respective tabs. The files will appear in the ```Downloads``` folder of the app directory (```GMOCU.app/Contents/Resources/Downloads``` for macOS or ```gmocu/Downloads``` for Windows).

#### Data import

Import data from another ```gmocu.db``` file together with the associated nuclei acid features and organisms if they are not yet present in the glossary of the app. This function is useful for combining data from several users into one database file. See the [video tutorial](####data-import-from-another-gmocu-instance).

### Backup

To backup the database it suffices to copy the ```gmocu.db``` SQLite database file located under ```GMOCU.app/Contents/MacOS``` for macOS releases or in the ```gmocu``` folder for Windows releases. The file contains all relevant data. It is possible to store the ```gmocu.db``` file at a location which is synced via a cloud service such as Dropbox. Then, replace the file in the application folder with a softlink to that file. That way, one can work with the same database from different computers. Regular backup recommended.

### Manual data editing

The data stored in tables within the `gmocu.db` file can be accessed by software such as [DB Browser for SQLite](https://sqlitebrowser.org/). While we generally recommend to refrain from manual editing, it might by required in particular cases.

### Link to the public regestry jbei/ICE database

Make a free account at https://public-registry.jbei.org/. Generate an access token in the account settings and add it in the GMOCU settings tab. Note that you may not be able to delete entries again from the registry. Alternatively, install a local jbei/ICE instance (recommended, [see below](##install-jbei/ice-as-docker-container-locally-or-on-a-server)).

### Hidden settings

### Specify scaling and fontsize and reset OS-dependent detection

In the Settings tab, the fields for defining fontsize and scaling are inactivated (greyed out). Enable them by pressing the key combination ```Ctrl + e```. Now you can specify the values and save. Restart GMOCU.

In order to reset the OS-dependend automated setting of the font size and scaling values, enter ```__``` (double underscore) into the fields and save. Close GMOCU and delete the file ```gmocu.json``` in the project directory. Restart GMOCU.

## Install jbei/ICE as docker container locally or on a server

- For reference, see [https://github.com/JBEI/ice/tree/trunk/docker](https://github.com/JBEI/ice/tree/trunk/docker).
- Install Docker Desktop, set startup after login in settings.
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
- Eiter enter the static IP address set above into the docker-compose.yml file:
  
  ```yaml
  134.99.70.14:9999:8080
  ```
  
  or leave the address as localhost for installation on a local machine without network access:
  
  ```yaml
  127.0.0.1:9999:8080
  ```
- Install jbei/ICE from docker hub, create containers and launch:
  
  ```bash
  docker pull jbei/ice
  docker-compose up
  ```
- Call the address set above in a browser and login with "Administrator" as user and password.
- Create a new user account and setup the access token to use in the GMOCU settings.

### Possible backup solution for docker volumes

Install [docker-vackup](https://github.com/BretFisher/docker-vackup).

Script the following commands and execute them e.g. daily.Incude the tarballs into your regular backup solution:

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

conda install PySimpleGUI pandas Pillow xlsxwriter openpyxl
pip install icebreaker pyinstaller
```

Deploy executable using Pyinstaller:

```python
conda activate gmocu
pyinstaller gmocu.spec
```

## Resources

- [PySimpleSQL](https://github.com/PySimpleSQL)
- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [ICEbreaker](https://edinburgh-genome-foundry.github.io/icebreaker/)

