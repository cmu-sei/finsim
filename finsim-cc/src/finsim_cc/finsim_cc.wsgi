#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

#WSGI config file is divided into activating the virtualenv and importing the Flask app as an application for Apache
#WSGI is important to use with Apache in order to deploy the Flask app as a production server
import os, sys

#Ensure that the path for activate_this matches where activate_this.py is for virtualenv
#Without this, the wrong versions of libraries or python may be used, which screws up the project
activate_this = '/var/www/finsim-cc/src/finsim_cc/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

#Make sure the path matches here. Went a level up so that it refers to the folder containing the Flask code
sys.path.insert(0, '/var/www/finsim-cc/src/')
from finsim_cc import app as application
