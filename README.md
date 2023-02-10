# GMOCU

Plasmid database with GMO documentation.

## Download

Download GMOCU for macOS and Windows from the [Releases](https://github.com/beyerh/gmocu/releases) page.

## Settings

| Setting          | Description                                                                                                                                                                                                                                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initials         | Define the user or project initials. Based on the entry, a folder on jbei/ICE will be generated into which plasmid entries will be uploaded. The initials should not and cannot be changed anymore at a later date.                                                                                                                                      |
| GMO institute    | Provide governmental information on the GMO facility (Az. and Anlage Nr.) which will appear on the Formblatt Z.                                                                                                                                                                                                                                          |
| jbei/ICE API     | Generate an API key for a shared jbei/ICE account either hosted locally or on the public server. Enter the key. Several accounts can be added in order to push plasmid data into multiple accounts if desired.                                                                                                                                           |
| Google Sheet ID  | Google Sheet ID: Upload the glossary file ```GDrive_glossary.xlsx``` to a Google Drive account and make it public. Extract the identifier code from the link and enter. E.g.: Link: ```https://docs.google.com/spreadsheets/d/16h5mFdL_k0W5QYokuryDY2-76czxFrOPachmz8W4a5s/edit#gid=0```, Identifier: ```16h5mFdL_k0W5QYokuryDY2-76czxFrOPachmz8W4a5s``` |
| Style            | Visual theme.                                                                                                                                                                                                                                                                                                                                            |
| Duplicate GMOs   | When duplicating a selected plasmid, GMOs will also be copied, however, with the current date. (Default, false)                                                                                                                                                                                                                                          |
| Upload completed | Only upload plasmid entries that were set to the status "Complete". (Default, false)                                                                                                                                                                                                                                                                     |
| Target organisms | Define target organisms (working organisms for GMO generation). The organisms must first be present in the organism glossary.                                                                                                                                                                                                                            |
| Fav. organisms   | Select some of the target organisms for generating several GMOs with one click using the ':)' convenience function. All organisms in ```Fav. organisms``` must be present in ```Target organisms```.                                                                                                                                                     |

## Glossaries

The ```Nucleic acids``` and ```Organisms``` glossaries can be imported and exported from and to ```*.xlsx``` files in the respective tabs. Another convenient way to manage the glossaries is to uplad the the ```GDrive_glossary.xlsx``` file to an Google Drive account, make the access public, and set the Google Sheets ID in the Settings tab (see section Settings). Entries can now be imported using the button ```Add entries from Google Sheet which not yet exist```.

## Plasmid data

Enter plasmid data and GMOs in the ```Plasmid data``` tab. There are also functions for uploading Genebank plasmid maps and associated data. The plasmid maps will be added to jbei/ICE on upload. There are several convenience functions for adding GMO-relevant Cassettes and GMO entries. Please import ```Nucleic acids``` and ```Organisms``` glossaries and fill in all ```Settings``` before starting to add data.

## GMO and Maintainance

### Maintenance

Check for completness of the glossaries and for duplicates of plasmid entries.

### jbei/ICE

Upload plasmid entries to jbei/ICE. Each upload will overwrite the information on the server. When ```Only new plasmids``` is checked, GMOCU will only upload entries with plasmid names which do not yet exist in the respective folder on the ICE server. Another way to update the information of a single plasmid, e.g. after edit is by pressing the ```ICE``` button on the top right corner in the ```Plasmid data``` tab.

### GMO

Generate a simple ```plasmid list``` or the ```Formblat Z``` required for the governmental regulations. Also export the ```Nucleic acids``` and ```Organisms``` in the respective tabs. The files will appear in the ```Downloads``` folder of the app directory (```GMOCU.app/Contents/Resources/Downloads``` for macOS or ```gmocu/Downloads``` for Windows).

### Data import

Import data from another ```gmocu.db``` file together with the associated nuclei acid features and organisms if they are not yet present in the glossary of the app. This function is useful for combining data from several users into one database file.

## Backup

To backup the database it suffices to copy the ```gmocu.db``` SQLite database file located under ```GMOCU.app/Contents/MacOS``` for macOS releases or in the ```gmocu``` folder for Windows releases.

## Link to the public regestry jbei/ICE database

Make a free account at https://public-registry.jbei.org/. Generate an access token in the account settings and add it in the GMOCU settings tab. Note that you may not be able to delete entries again from the registry. Alternatively, install a local jbei/ICE instance (see below).

## Hidden settings

### Specify scaling and fontsize and resed OS-dependent detection

In the Settings tab, the fields for defining fontsize and scaling are inactivated (greyed out). Enable them by pressing the key combination ```Ctrl + e```. Now you can specify the values and save. Restart GMOCU.

In order to reset the OS-depented automated setting of the font size and scaling values, enter ```__``` (double underscore) into the fields and save. Close GMOCU and delete the file ```gmocu.json``` in the project directory. Restart GMOCU.

## Install jbei/ICE as docker container on server

- For reference, see [https://github.com/JBEI/ice/tree/trunk/docker](https://github.com/JBEI/ice/tree/trunk/docker).

- Install Docker Desktop, set startup after login in settings.

- Set static IP in Network Settings and change the computer name for network access via ```name.local```.

- Clone repo:
  
  ```bash
  git clone https://github.com/beyerh/gmocu.git
  ```

- Copy modified docker-dompose.yml containing PASSWORD fix and autostart:
  
  ```bash
  mkdir ice
  cp gmocu/docker-compose.yml ice/
  cd ice
  ```

- Replace static IP address in the docker-compose.yml file with the address set up above:
  
  ```yaml
  134.99.70.14:9999:8080
  ```

- Install jbei/ICE from docker hub, create containers and launch:
  
  ```bash
  docker pull jbei/ice
  docker-compose up
  ```

- Login with "Administrator" as user and password.

- Create a new user account and setup the access token.

### Possible backup solution for docker volumes

install [docker-vackup](https://github.com/BretFisher/docker-vackup)

Script the following commands and execute them e.g. daily.Incude the tarballs into your regular backup solution:

```bash
cd ~/ &&
/usr/local/bin/vackup export ice_ice_home ice_ice_home.tar.gz &&
/usr/local/bin/vackup export ice_ice_index ice_ice_index.tar.gz &&
/usr/local/bin/vackup export ice_postgres_db ice_postgres_db.tar.gz
```

You may execute the the backup commands via an automator app on macOS (this requires including the `PATH` variable in the script `PATH=$PATH:/usr/local/bin`) and schedule with the calendar app. Alternatively a corn job executed as user might work.

## Anaconda development environment

With anaconda installed, add the conda-forge repository:

```python
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Set up the developmental ```gmocu``` environment:

```python
conda create --name gmocu python=3.9
conda activate gmocu

conda install PySimpleGUI pandas Pillow xlsxwriter
pip install icebreaker https://github.com/pyinstaller/pyinstaller/tarball/develop

pip uninstall requests-cache
pip install --pre requests-cache
```

## Resources

- [PySimpleSQL](https://github.com/PySimpleSQL)

- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)