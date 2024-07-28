# MotoGP calendar TV8 scraper

## Introduction

MotoGP calendar TV8 scraper is a python function that scrapes all the information from the TV8 website about their scheduling of MotoGP events and saves them in a SQLite DB.

## Functioning

This process is very simple and it's made possible by the __beautifulsoup4__ python package. It starts from the TV8 MotoGP main page and then scrapes all the events scheduled by the keyword "Gran Premio".

Then searches for each of that GP events the link of the GP and scrape the event information from that page.

At the end all the data extracted from the website will be saved in a SQLite DB. SQLite has been choosed due to the limited capacity of the server where this process will run. If, by any reason, there is someone that wants to implements other DB connections and integrations it's well accepted.

The lifecycle of this process will be logged in a file. This file, suffix and location, can be specified in the __.env__ file (as for the SQLite DB file).
The log files will not be deleted automatically and for each new day of execution will be created a new file.

## Environment file

You need to adjust the __.env__ file for the process to run successfully. This has a few configuration:

* __LOG_PATH__, the absolute path where the LOGS are going to be saved.
* __LOG_FILE_SUFFIX__, the suffix of the log file (es. 2024-07-28-SUFFIX.log).
* __SQLITE_DB_PATH__, the absolute path where the SQLite DB path is located. If none it's specified or the directory is empty a new one will be created.

## Legal

This function, before scraping any data, will search in the __robots.txt__ file if it can parse any of the requested page.
