#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

Financial Simulator 2.0 - Demo 1 Set-up and Guide
Updated AO 24 Jan 2019

Brief:
- Basic demonstration of the functionality available so far for FinSim 2.0
- Utilizes 3 Flask apps (1 finsim-cc, and 2 finsim-trans)
- Utilizes 2 Angular apps (each correspond to a finsim-trans Flask app)
- 3 databases (Mysql: cc, trans, trans2)
- 2 Python scripts (demo_init.py, demo_gen_trans.py)
- If you have already run through this before and want a clean slate, simply drop the tables of all 3 databases (cc, trans, trans2) before starting up again

Environment:
- All on localhost, using different ports
- Port 5000 for finsim-cc
- Port 10000 for finsim-trans
- Port 10100 for finsim-trans2
- Port 4200 for finsim-web
- Port 4210 for finsim-web2
- ports/login info/urls/prefixes are all hard-coded into each app

Setup Guide:
- [Assuming access to the gitlab repositories is available]
- Pull the repositories to local machine
- cp -r finsim-trans finsim-trans2
- cp -r finsim-web finsim-web2
- For finsim-cc, finsim-trans, and finsim-trans2, follow the README steps to make sure that the mysql databases are set-up (cc, trans, and trans2) and virtualenv is used
- For finsim-trans2:
    - [Assuming you already followed the steps in readme for first time environment set-up...including pip, mysql, virtualenv]
    - resources.py:
        - line 11: change bankUser to 'bnk_001'
        - line 15: change localPrefix to '001'
    - run.py:
        - line 10: change app.config['SQLALCHEMY_DATABASE_URI'] value to 'mysql://trans2:@localhost/trans2'
- For finsim-web2:
    - /src/index.html:
        - line 5: change title from "FinsimWeb" to "FinsimWeb2" to easily differentiate during demo
    - /src/app/fin-sim.service.ts:
        - line 103: update private port variable from 10000 to 10100

Start-up the apps:
- . /venv/bin/activate for all 3 Flask apps
- FLASK_RUN_PORT=X FLASK_APP=run.py FLASK_DEBUG=1 flask run
    - Refer to Environment of this guide to replace x with the appropriate port used for each flask app
- ng serve
    - For finsim-web
- ng serve --port 4210
    - For finsim-web2
- Check each terminal to make sure they are up and running normally or compiled successfully
- Open a browser and open two connections to each Angular app (localhost:4200 and localhost:4210)

Demonstration Init:
- open another terminal and cd to finsim-cc, where the demo scripts are
- run demo_init.py
- Login to jjones/jjones2 via your browser to each Angular app to demonstrate the /accounts and /account?number= pages
    - You should see 3 accounts for both jjones on finsim-web and jjones2 on finsim-web2

Demonstration Transactions:
- run demo_gen_trans.py
- Login to jjones/jjones2 via your browser to each Angular app to demonstrate the /accounts and /account?number= pages
    - You should see transactions for 879 and 880 accounts for both jjones on finsim-web and jjones2 on finsim-web2
- You can login as target on finsim-web to see the two transactions
    - $1000 from jjones 879 [local transaction]
    - $1001 from jjones2 879 [bank-to-bank transaction]
- You can login as amazon on finsim-web2 to see the two transactions
    - $2000 from jjones 880 [bank-to-bank transaction]
    - $2001 from jjones2 880 [local transaction]
