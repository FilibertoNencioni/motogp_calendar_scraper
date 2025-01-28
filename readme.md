# MotoGP calendar scraper

## Introduction

MotoGP calendar scraper is a Python function that collects and aggregates all the MotoGP broadcasts emitted by the official broadcaster and other private / public broadcasters.

All the information this process saves is meant to be displayed by a mobile application, where everyone can see if their provider will broadcast the event live or not and at what time.

This project is meant to be open and accessible to everyone, so that everyone (within the respect of the laws) will scrape all the MotoGP broadcasters events and saves them ready to be viewed by the users.

## Functioning

It works through "processes" where everyone identifies a different broadcaster. The first and main process is the [MotoGP service](./src/services/motogp_service.py) which will save (or update) all the main broadcasts and additional info such as circuit details, etc. Only when this has finished will all the other "side" processes start.

Those processes *can only obtain broadcast information* and save it in the **Broadcast** table (attached to its corresponding event).

The lifecycle of the main and sub processes will be logged in a file. This file, suffix and location can be specified in the [**.env file**](.env.test) file.
The log files will not be deleted automatically (unless a retention policy is specified in the .env file) and for each new day of execution, a new file will be created.

## Prerequisites

* MySQL DB (tested with v8.4)
* Python (tested with v3.12.3)

## Setup

### Database

Make sure you have a MySQL instance running and all the connection details are typed in the environment file. Then check if your database structure corresponds to the one written [here](./sql/init-db.sql).

### Python requirements

You can install Python packages using [requirements file](./requirements.txt) by typing the following command in the root folder of this project.

```shell
pip install -r ./requirements.txt
```

## Environment file

You need to adjust the __.env__ file for the process to run successfully. This has a few configurations:

### Logs

* LOG_PATH, ***optional***, *Path where the log files have to be saved. Default is: ``project_directory/logs``*
* LOG_FILE_SUFFIX, ***optional**, Those log files are saved daily with a date prefix in the format "yyyy-mm-dd", If you want to add some text after the date, you can specify it here*
* LOG_DAYS_RETENTION, ***optional**, Indicates the date range you want to keep the logs, it must be expressed as a number of days (int), for example, 30 (for a month)*
* LOG_MAX_FILES= ***optional**, Indicates the maximum number of log files you want to keep*

### Database

* DB_HOST=
* DB_USER=
* DB_PASSWORD=
* DB_NAME=

### Misc

* ASSETS_FOLDER_PATH, *At the moment, this is not managed*

## Legal

This function, before scraping any data, will search in the **robots.txt** file to see if it can parse any of the requested pages.
