#!/bin/bash

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

#Need to incorporate vmtools somehow


#Steps for init:
#- Configure network info
#- Generate db
#- Run python script
#- Populate db via requests? <This might be a part of python script instead>

#Steps for run
# Note that it will have to be changed to be used for production servers
#- Run script(s) and/or start servers

#Steps for clean
# Clear databases
# Stop servers?
# Stop scripts?
 
activate () {
    source venv/bin/activate
}

if [ $# -eq 0 ]; then
    echo "Run this script specifying either init or run"
else
    if [ "$1" = "init" ]; then
        echo "Called with init param"
        python init_script.py --s 42 --b 2 --c 1 --m 2 --u 100 --w b0 --f /home/url_list.txt --p 1 --r 0
    elif [ "$1" = "run" ]; then
        echo -e "Called with run param. Virtualenv is being used\n\n"
        activate
        #UPDATE THIS WHEN YOU WANT TO USE A DIFFERENT FLASK APP
        FLASK_RUN_PORT=10000 FLASK_APP=../finsim-trans/run.py FLASK_DEBUG=1 flask run
    elif [ "$1" = "clean" ]; then
        echo "Called with clean param. Currently commented out. Only clears cc/trans/trans2"
        #mysql clear_tables.sql
    else
        echo "Invalid param"
    fi

fi
