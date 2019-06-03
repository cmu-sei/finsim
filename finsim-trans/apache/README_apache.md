#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.


# Documentation for Apache with Flask for finsim-trans

- Consult the /src readme to make sure you have the right libraries downloaded, using venv
-  Checklist of things to potentially change in apache config file:
    - Ensure that WSGIDaemonProcess user=finsim matches a user that exists on your system (same for ServerAdmin entry)
    - Ensure that the path of your WSGI file matches the path found here
    - Ensure that the path to the Flask app code matches what you use for the Directory section
    - Ensure that the aliasing for the Angular code is the correct path

- Enable the app for finsim_trans to be deployed on the Apache server by running
    - `sudo a2ensite finsim_trans`

- Start Apache server by running
    - `sudo systemctl enable apache2`
    - `sudo systemctl start apache2`

- Consult the documentation for the WSGI file to ensure that it works correctly
- Consider adjusting the logging level in `finsim_trans.conf` when debugging the apache server

# Steps to use self-signed ssl cert
- `openssl req -new -x509 -nodes -out <name>.crt -keyout <name>.key`
    - It is primarily important that for the FQDN you enter the url/ip address you are using for finsim-cc
    - Enter input for each description field or "."
- Enable ssl for apache2
    - `a2enmod ssl`
    - Then restart apache
- Make sure all uses of the Python requests library specifies `verify=False` as one of the parameters if using a self-signed ssl cert
    - i.e. `requests.post(..., verify=False)`
- If you do use this for an actual production environment, use a public CA rather than self-signed certs!
    - Also make sure that all uses of Python requests library does **NOT** use `verify=False`
- Make sure the paths listed for the certificate and key files are correct
- For apache finsim_trans config file
    - Edit VirtualHost port to 443, not 80
    - `SSLEngine on`
    - `SSLCertificateFile /etc/ssl/crt/trans-us.crt`
    - `SSLCertificateKeyFile /etc/ssl/crt/trans-us.key`
