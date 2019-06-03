#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
#helper functions
### ---

from finsim_trans.init_script import gen_all_data, handle_current_component
import requests, subprocess

## ---
# @brief bnk_login used by finsim-cc to login to finsim-trans
# @input url, bnkUser, bnkPass - login to component specified by url with bnk credentials
# @return token - access token to authenticate to the component specified by url
## ---
def bnk_login(url, bnkUser, bnkPass):
    loginForm = { "username":bnkUser, "password":bnkPass }
    token = requests.post( url + "login", json = loginForm, verify=False ).json()
    return token

## ---
# @brief check_login_list obtains the current component's login data and urls for the other components it needs to be able to connect to
#  calls use_vmtools
# @return current_component
## ---
def check_login_list():
    args_list = []
    gen_all = []
    current_component = []

    args_list = use_vmtools()
    if len(args_list) == 0:
        #issue with vmtoolsd calls
        return []
    gen_all = gen_all_data( str(args_list[0]), int(args_list[1]), int(args_list[2]), int(args_list[3]), int(args_list[4]), args_list[6] )
    if len(gen_all) == 0:
        #issue with gen_all_data call
        return []
    current_component = handle_current_component( gen_all, args_list[5], int(args_list[1]), int(args_list[2]), int(args_list[3]), register_to_db=False, return_all=False )
    if len(current_component) == 0:
        return []
    return current_component

## ---
# @brief use_vmtools is called by check_login_list to get the init_script param values
#  intent is to have the param values obtained from vmtoolsd values, but currently hardcoded

#args list will be:
# 0 - rand_seed
# 1 - num_banks
# 2 - num_ccs
# 3 - num_mercs
# 4 - num_users
# 5 - whoami
# 6 - url_list_filepath
## ---
def use_vmtools():
    args_list = []
    '''
    rand_seed_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.rand_seed'"], stdout=subprocess.PIPE)
    args_list.append(str(rand_seed_proc.stdout, encoding="utf-8").replace("\n", ""))
    num_banks_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.num_banks'"], stdout=subprocess.PIPE)
    args_list.append(str(num_banks_proc.stdout, encoding="utf-8").replace("\n", ""))
    num_ccs_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.num_ccs'"], stdout=subprocess.PIPE)
    args_list.append(str(num_ccs_proc.stdout, encoding="utf-8").replace("\n", ""))
    num_mercs_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.num_mercs'"], stdout=subprocess.PIPE)
    args_list.append(str(num_mercs_proc.stdout, encoding="utf-8").replace("\n", ""))
    num_users_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.num_users'"], stdout=subprocess.PIPE)
    args_list.append(str(num_users_proc.stdout, encoding="utf-8").replace("\n", ""))
    whoami_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.whoami'"], stdout=subprocess.PIPE)
    args_list.append(str(whoami_proc.stdout, encoding="utf-8").replace("\n", ""))
    url_list_filepath_proc = subprocess.run(["vmtoolsd --cmd 'info-get guestinfo.url_list_filepath'"], stdout=subprocess.PIPE)
    args_list.append(str(url_list_filepath_proc.stdout, encoding="utf-8").replace("\n", ""))
    '''
    #Using hard-coded values for the sake of getting this ready asap
    args_list.append('3')
    args_list.append(1)
    args_list.append(1)
    args_list.append(1)
    args_list.append(50)
    args_list.append("b0")
    args_list.append("/home/url_list.txt")
    return args_list
