#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

# FinSim Merchant

## Brief
- FinSim-merch acts as a merchant - generates transactions with user accounts

##Quick Usage:

### For development environments, see below

### For production environments, be sure to follow the steps below on making FinSim-merch work on startup

#### First time set-up:

- If you have not already done so, follow the Initial Setup instructions in the main README to download all of the necessary libraries and dependencies

- Steps to follow to make merchant work on startup:
    - `chmod +x run_merchant.sh`
    - `chmod 664 /etc/systemd/system/run_merchant.service`
    - `systemctl daemon-reload`
    - `systemctl enable run_merchant.service`
    - `systemctl start run_merchant.service`

#### Quick set-up after the first time:
- If you are running merchant.py on its own, ensure you use virtualenv to use the right versions
    - `. venv/bin/activate`
- Double check the paths listed for venv and merchant.py/run_merchant.sh in run_merchant.sh/run_merchant.service are correct
    - For an example deployment, each file had the following paths:
        - `run_merchant.service`: `/etc/systemd/system/run_merchant.service`
        - `run_merchant.sh`: `/var/www/finsim/finsim-merch/run_merchant.sh`
        - `merchant.py`: `/var/www/finsim/finsim-merch/merchant.py`
- If running merchant.py on startup using the systemd script:
    - `systemctl start/stop/restart run_merchant` to handle the systemd script for finsim-merch
    - `systemctl status run_merchant` to check the activity of finsim-merch
- Note:
    - Ensure that if you are running merchant.py on its own, to activate virtualenv and use python3 to run merchant.py
    - merchant.py is currently using hard-coded values. The plan is to switch to `vmtoolsd` commands to make it easier to deploy and/or adding an additional script that will use a master text file for configuration

## Overview
- `merchant.py`: Main functionality of merchant component
- `run_merchant.sh`: Activates virtualenv and runs `merchant.py`
- `run_merchant.service`: Systemd startup script that will run `run_merchant.sh` on startup
- `init_script.py` (symlink): Used by finsim-merch to get the accounts and login info necessary to interact with finsim-cc and trans



