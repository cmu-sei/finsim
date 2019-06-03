FinSim

Copyright 2018 Carnegie Mellon University. All Rights Reserved.

NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.

Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

# FinSim Transaction Server

## Brief:
- FinSim-trans acts as a bank - processes transactions passed on from FinSim-cc and holds account information, allowing for deposits/withdrawals


## Quick Usage:

### For development environments, see below

### For production environments, be sure to also go through README_apache.md and the comments in finsim_trans.wsgi

#### First time set-up:

- If you have not already done so, follow the Initial Setup instructions in the main README to download all of the necessary libraries and dependencies

#### Quick set-up after the first time:
- To run this flask app in DEVELOPMENT mode:
    - `. venv/bin/activate`
    - `FLASK_RUN_PORT=10000 FLASK_APP=__init__.py FLASK_DEBUG=1 FLASK_ENV=development flask run`
- To run this in PRODUCTION mode:
    - UPDATE the SECRET_KEY and JWT_SECRET_KEY values used in `/src/finsim-trans/__init__.py`
        - This is very important before finsim-trans is deployed as a production server
    - Refer to the README_apache.md file on additional documentation
    - Double-check the paths listed in the apache config file and the wsgi config file to make sure they have the correct path of the finsim-trans code
    - Generate a certificate and replace the configuration in the apache config file to use the certificate, as well as the `/home/url_list.txt` entries to use https instead of http
    - `systemctl start/stop/restart apache2` to handle the production server for finsim-trans
    - refer to the access and error logs for apache2 to monitor the server (paths listed in the apache config file)
- NOTE:
    - Currently using self-signed certificates for the apache server
    - `helper.py` is currently using hard-coded values. The plan is to switch to vmtoolsd commands to make it easier to deploy and/or adding an additional script that will use a master text file for configuration


## Overview:

### /apache

- Apache config file for finsim-cc and documentation to follow on setting it up

### /src/finsim_trans

#### /old
- contains demo code or files that are not currently used

#### /test
- scripts used to test finsim-cc endpoints and general functionality

#### finsim_trans.wsgi
- WSGI config file. This is important for deployment to a production server

#### __init__.py
- Formerly the "run.py" file, is the main file for the Flask application

#### models.py, resources.py, views.py
- Key components of Flask project code
- (In order) Database backend/schema, endpoints for finsim-trans, frontend of Flask (not important - only "Hello World" as an initial test of server connectivity)

#### helper.py, init_script.py (symlink)
- `helper.py` creates a helper function to login to banks to optimize code
- `helper.py` also uses functions in `init_script.py` to grab component login data and etc in order to communicate with other components
- `init_script.py` generates and can populate databases with all of the account information and login info needed for each component based on a random seed for Faker and Random libraries
- `init_script.py` is critical for setup prior to deployment! Run `python3 init_script.py --h` to learn how to use it

#### bnk_000_log.txt
- Logging used primarily in development mode
