## Overview
This script is a client for API https://appcenter.ms/.
The script creates builds for every branch and print the result.
If there isn't a built config, the script creates a new config from the file.
## Install and Requirements
The script can work with python3 and use several libraries.
To install libs you can run this command:
`pip3 install requests click iso8601`
and clone this repository.
## Launch
To use this script you can run these commands:
- create and run builds 
    `python appcenter_builds.py start_build --app_name {app name} --owner_name {account name}  --token {your full access token} --config_file {path to config file}`;
- print build result
   `python appcenter_builds.py print --app_name {app name} --owner_name {account name} --token {your read access token}`;
