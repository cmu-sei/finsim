#!/bin/bash

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

# Register a bank
curl localhost:5000/registration -H "Content-Type: application/json" -d '{"username":"pnc","password":"pncpass","role":"BANK"}'
# Log in
TOKEN=$(curl -s localhost:5000/login -H "Content-Type: application/json" -d '{"username":"pnc","password":"pncpass"}'|jq --raw-output .'access_token')

# Get the secret, then create an account, then withdraw some money
curl localhost:5000/secret -H "Authorization: Bearer $TOKEN"
#curl localhost:5000/account/create -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"owner_id":1,"number":"1234123456785678"}'
curl localhost:5000/bank/withdrawal -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"owner_id":1,"account":"1", "amount": 99.9}'
