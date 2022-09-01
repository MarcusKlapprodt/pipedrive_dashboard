# Pipedrive Dashboard
The purpose was to display kpi metrics for customer success managers, based on their daily activities. 
(now that we switched to hubspot, we don't need the dashboard anymore, but maybe it helps others)

## Table of contents
 - Readme
 - CS Dashboard --> Overview with pandas and plotly
 - CS Simplified Dashbaord --> Get a brief table of activities
 - pipedrive Connector --> Collection of functions to get the api key, the users, table structure, fortmatting of charts, ...
 - requirements.txt
 - .gitignore

## How to install
 - clone the repository
 - set up venv with `python 3.9`
 - pip install -r requirements.txt
 - store your api-key in a `.key.json` file (might be deprecated by Pipedrive in the future)
 - store user keys in `/keys/users.json`
