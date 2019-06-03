#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

from faker import Faker
import yaml
import requests, random, sys, argparse

#Script to generate usernames/passwords given a random seed and parameters
#Layout of script:
#	parse arguments
#	read from url textfile for banks and ccs
#	generate banks
#	generate ccs
#	generate merchants
#	generate users
#	check --w/who and collect from lists what the component needs
#	populate current component db with the specific list


'''
ToDo:
- need hostname:port associated with every cc and bank somehow (vmdktools?)
	- currently we just have a textfile with component and ip addr tuples, line by line
- Low priority tasks:
	- argument to specify max number of accounts a user can have
		- does not have to be an equal distribution
	- switch it up so that a user can have bank accounts with multiple banks?
	- specific username accounts for each cc_processor, bank, merchant rather than using the name?
		- may be sufficient to just remove whitespace and lowercase for all

steps:
- config data to CC and bank
	- banks need prefixes assigned to them
- Create accounts
- Create list based on current component running
'''
#15 credit card processors from https://marketingland.com/top-10-payment-processing-companies-world-175913 and https://www.business.com/categories/best-credit-card-processing/
cc_processors = [ "PayPal", "Due", "Stripe", "Flagship Merchant Services", "Payline Data", "Square", "Adyen", "BitPay", "GoCardless", "Cayan", "Helcim", "First Data", "TSYS", "Fattmerchant", "Worldpay" ]

#First 50 banks from https://en.wikipedia.org/wiki/List_of_largest_banks_in_the_United_States
banks = [ "JPMorgan Chase", "Bank of America", "Citigroup", "Wells Fargo", "Goldman Sachs", "Morgan Stanley", "U.S. Bancorp", "TD Bank, N.A.", "PNC Financial Services", "Capitol One", "The Bank of New York Mellon", "TIAA", "HSBC Bank USA", "Charles Schwab Corporation", "State Street Corporation",  "BB&T", "SunTrust Banks", "American Express", "Ally Financial", "State Farm", "MUFG Union Bank", "USAA", "Citizens Financial Group", "BMO Harris Bank", "Barclays", "Fifth Third Bank", "KeyCorp", "UBS", "Northern Trust", "Santander Bank", "Credit Suisse", "BNP Paribas", "Regions Financial Corporation", "Deutsche Bank", "RBC Bank", "M&T Bank", "Discover Financial", "Huntington Bancshares", "Synchrony Financial", "BBVA Compass", "Comerica", "E-Trade", "Zions Bancorporation", "Silicon Valley Bank", "New York Community Bank", "CIT Group", "Popular, Inc.", "People's United Financial", "Mutual of Omaha", "Mizuho Financial Group", "First Horizon National Corporation" ]


#Have all of the generation done here
#if we start seeding in the function every time, it should generate the same set of data for the same seed everytime
def gen_all_data( rand_seed, num_banks, num_ccs, num_mercs, num_users, url_list_filepath ):
    gen_all = []
    gen_banks = []
    gen_ccs = []
    gen_mercs = []
    gen_users = []
    bank_prefixes = []

    #USED TO MAKE SURE THE SAME PYTHON VERSION IS USED ACROSS ALL FINSIM COMPONENTS
    #It is critical that the same python version is used by every component
    print(sys.version)
    fake = Faker()
    fake.seed(rand_seed)
    random.seed(rand_seed)

    f = open(url_list_filepath, 'r')
    num_bank_urls = 0
    num_cc_urls = 0
    #Need to then parse through to add bank/cc pairs with their to-be-generated data
    #Idea is we have the bN/cN (b = bank, c = cc) url tuples listed line by line
    for line in f:
        component = line.split(" ")[0]
        url = line.split(" ")[1].replace("\n", "")
        cur_component = [component, url]
        if component[0] == 'b' and (num_bank_urls < num_banks):
            gen_banks.append(cur_component)
            num_bank_urls += 1
        elif component[0] == 'c' and (num_cc_urls < num_ccs):
            gen_ccs.append(cur_component)
            num_cc_urls += 1
    f.close()

    #print( "\n\nGenerating banks" )
    #print( "In format of: component_id, url, bank_id, username, list of [bank_id, url, password], bank_prefix\n" )
    bank_ctr = 0
    for bank in random.sample(banks, num_banks):
        gen_banks[bank_ctr].append( bank_ctr )
        gen_banks[bank_ctr].append( bank.replace(" ", "").lower())
        bank_pws = []
        #Generate a password for this current bank to be used at every other bank
        for j in range(num_banks):
            if j != bank_ctr:
                cur_pw = []
                cur_pw.append( int(j) )
                cur_pw.append( gen_banks[j][1] )
                cur_pw.append( str(fake.password()) )
                bank_pws.append(cur_pw)
            else:
                bank_pws.append(["CURRENT_BANK"])
        gen_banks[bank_ctr].append( bank_pws )
        cur_bank_prefix = random.randint(100, 999)
        gen_banks[bank_ctr].append( cur_bank_prefix )
        bank_prefixes.append ( cur_bank_prefix )
        bank_ctr+=1
    #print( yaml.dump( gen_banks ) )
    #print( bank_prefixes )
    for i in range(num_banks): #Loop through gen_banks
        for j in range(num_banks): #Loop through each bank's list of other bank's info
            if j != i: #We don't need current bank to add its own info to list
                #Add username (universal) and password (that this other bank would use to login to current bank) to end of other_bnk list of current bank
                gen_banks[i][4][j].append( gen_banks[j][5] )
                gen_banks[i][4][j].append( [ gen_banks[j][3], gen_banks[j][4][i][2] ] )    
    gen_all.append( gen_banks )

    #print( "\n\nGenerating cc processors" )
    #print( "In format of: component_id, url, cc_id, username, list of [bank_id, password]\n" )
    cc_ctr = 0
    for cc in random.sample(cc_processors, num_ccs):
        gen_ccs[cc_ctr].append( cc_ctr )
        gen_ccs[cc_ctr].append( cc.replace(" ", "").lower() )
        #cc login for every bank
        bank_pws = []
        for i in range(num_banks):
            cur_pw = []
            cur_pw.append( int(i) )
            cur_pw.append( str(fake.password()) )
            bank_pws.append(cur_pw)
        gen_ccs[cc_ctr].append( bank_pws )
        cc_ctr+=1
    #print( yaml.dump( gen_ccs ) )
    gen_all.append( gen_ccs )

    #print( "\n\nGenerating merchants" )
    #print( "In format of: merchant_id, username, list of cc_info [password], list of bank_info [bank_acct, password]\n" )
    for i in range(num_mercs):
        cur_merc = []
        cur_cc_info = []
        cur_bnk_info = []
        cur_merc.append( i )
        cur_merc.append( str(fake.company().replace(" ", "").lower()) )
        cur_cc_info.append( str(fake.password()) )
        cur_merc.append( cur_cc_info )
        fixed_acct = str(bank_prefixes[i%len(bank_prefixes)]) + str(fake.credit_card_number(card_type = "visa"))[3:]
        cur_bnk_info.append( fixed_acct )
        cur_bnk_info.append( str(fake.password()) )
        cur_merc.append( cur_bnk_info )
        gen_mercs.append( cur_merc )
    #print( yaml.dump( gen_mercs ) )
    gen_all.append( gen_mercs )

    #print( "\n\nGenerating users" )
    #print( "In format of: user_id, username, password, list of acct_nums\n" )
    for i in range(num_users):
        cur_user = []
        cur_user.append( i )
        cur_user.append( str(fake.user_name()) )
        cur_user.append( str(fake.password()) )
        cur_accts = []
        for j in range(random.randint(1, 3)):
            fixed_acct = str(bank_prefixes[i%len(bank_prefixes)]) + str(fake.credit_card_number(card_type = "visa"))[3:]
            cur_accts.append( fixed_acct )
        cur_user.append( cur_accts )
        gen_users.append( cur_user )
    #print( yaml.dump( gen_users ) )
    gen_all.append( gen_users )

    return gen_all


#Do specific component tasks here
#register_to_db if the current component's database should be populated or not
#return_all if all component data should be returned or just what is necessary (excluding any accounts that would be added to the database)
def handle_current_component( gen_all, component_id, num_banks, num_ccs, num_mercs, register_to_db=False, return_all=False ):
    gen_banks = gen_all[0]
    gen_ccs = gen_all[1]
    gen_mercs = gen_all[2]
    gen_users = gen_all[3]
    current_component = []

    if component_id[0] == 'b' and int(component_id[1]) < num_banks:
        '''
        A bank needs the following:
        - It's own info
        - All cc info (mostly just the cc's login to it)
        - All merchants who have accts with it
        - All users who have accts with it
        '''
        merc_list = []
        user_list = []
        other_bnk_list = []
        current_component.append( gen_banks[ int(component_id[1]) ] )
        current_component.append( gen_ccs )
        for merc in gen_mercs:
            if str(current_component[0][5]) == merc[3][0][0:3]:
                merc_list.append( merc )
        current_component.append( merc_list )
        for user in gen_users:
            for acct in user[3]:
                if str(current_component[0][5]) == str(acct[0:3]) and user_list.count(user) == 0:
                    user_list.append( user )
        current_component.append( user_list )
        if register_to_db:
            for cc in current_component[1]:
                #Connect to bank and register the ccs
                userReg = {"username": cc[3], "password": cc[4][int(component_id[1])][1], "role": "CC"}
                regMessage = requests.post( current_component[0][1] + "registration", json = userReg, verify=False )
                print( "Reg Message: " + regMessage.text )
            for merc in current_component[2]:
                #Connect to bank and register the mercs. Register, login, create account for each merchant
                userReg = {"username": merc[1], "password": merc[3][1], "role": "USER"}
                regMessage = requests.post( current_component[0][1] + "registration", json = userReg, verify=False )
                print( "Reg Message: " + regMessage.text )
                loginForm = {"username": merc[1], "password": merc[3][1]}
                token = requests.post( current_component[0][1] + "login", json = loginForm, verify=False ).json()
                print( token['access_token'] )
                header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
                accountReg = { "number": "{}".format( merc[3][0] ) }
                accountResponse = requests.post( current_component[0][1] + 'account/create', json = accountReg, headers = header, verify=False )
                print( "Response Text: " + accountResponse.text )
            for user in current_component[3]:
                #Connect to bank and register the users. Register, login, create account(s) for each user
                userReg = {"username": user[1], "password": user[2], "role": "USER"}
                regMessage = requests.post( current_component[0][1] + "registration", json = userReg, verify=False )
                print( "Reg Message: " + regMessage.text )
                loginForm = {"username": user[1], "password": user[2]}
                token = requests.post( current_component[0][1] + "login", json = loginForm, verify=False ).json()
                print( token['access_token'] )
                header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
                for account in user[3]:
                    accountReg = { "number": "{}".format( account ) }
                    accountResponse = requests.post( current_component[0][1] + 'account/create', json = accountReg, headers = header, verify=False )
                    print( "Response Text: " + accountResponse.text )
            for bank in current_component[0][4]:
                #Connect to bank and register the other banks
                if bank[0] != "CURRENT_BANK":
                    userReg = {"username": bank[4][0], "password": bank[4][1], "role": "BANK"}
                    regMessage = requests.post( current_component[0][1] + "registration", json = userReg, verify=False )
                    print( "Reg Message: " + regMessage.text )
        if return_all:
            return current_component
        else:
            return current_component[0]

        '''
        Now need to figure out how to pass on the rest of the necessary info for bnk to function
        '''
    elif component_id[0] == 'c' and int(component_id[1]) < num_ccs:
        '''
        A cc needs the following:
        - It's own info (with bank urls added to the list of passwords)
        - All merchants associated with it (mostly just merc's login to it)
        '''
        current_component.append( gen_ccs[ int(component_id[1]) ] )
        merc_list = []
        for i in range(num_banks):
            current_component[0][4][i].insert(1, gen_banks[i][1])
            current_component[0][4][i].append(gen_banks[i][5])
        for i in range(num_mercs):
            if (int(gen_mercs[i][0]) % num_ccs) == int(component_id[1]):
                merc_list.append( gen_mercs[i] )
        current_component.append( merc_list )
        if register_to_db:
            for merc in current_component[1]:
                #Connect to cc and register the merchants
                userReg = {"username": merc[1], "password": merc[2][0], "bank_acct": merc[3][0]}
                regMessage = requests.post( current_component[0][1] + "registration", json = userReg, verify=False )
                print( "Reg Message: " + regMessage.text )
        if return_all:
            return current_component
        else:
            return current_component[0]
        '''
        Now need to figure out how to pass on the rest of the necessary info for cc to function (everything except for merchant information)
        '''
    elif component_id[0] == 'm' and int(component_id[1]) < num_mercs:
        '''
        A merc needs the following:
        - It's own info
        - The cc it uses
        - All bank id and url tuples
        - All user accts
        '''
        user_acct_list = []
        current_component.append( gen_mercs[ int(component_id[1]) ] )
        matching_cc = gen_ccs[ (int(component_id[1]) % num_ccs) ]
        current_component[0][2].insert( 0, matching_cc[0] )
        current_component[0][2].insert( 1, matching_cc[1] )
        for bank in gen_banks:
            if str(current_component[0][3][0][0:3]) == str(bank[5]):
                current_component[0][3].insert( 0, bank[0] )
                current_component[0][3].insert( 1, bank[1] )
                current_component[0][3].append( bank[5] )
        for user in gen_users:
            for acct in user[3]:
                user_acct_list.append(acct)
        current_component.append( user_acct_list )
        return current_component
        '''
        Merc doesn't have a database to initialize/populate
        '''
    else:
        print( "Invalid component specified - not doing anything further" )

#Parse args, seed the random generator, call gen_all_data, then code
def main():
    parser = argparse.ArgumentParser(description = "Generate accounts given a random seed for FinSim 2.0")
    parser.add_argument("--s", "--seed", help = "Random seed used to generate accounts")
    parser.add_argument("--b", "--banks", help = "Number of banks to generate")
    parser.add_argument("--c", "--cc_processors", help = "Number of credit card processors to generate" )
    parser.add_argument("--m", "--merchants", help = "Number of merchants to generate")
    parser.add_argument("--u", "--users", help = "Number of users to generate")
    parser.add_argument("--w", "--who", help = "Current component that is running the script")
    parser.add_argument("--f", "--file", help = "List of all component urls")
    parser.add_argument("--p", "--populate_db", help = "Toggle off (0) or on (1) to populate current component's database or not. Does not apply when current component is merchant")
    parser.add_argument("--r", "--return_all",  help = "Toggle off (0) or on (1) to return all info for current_component (includes all registered accounts) or just functionality info")
    args = parser.parse_args()
    print( args )

    gen_all = gen_all_data( args.s, int(args.b), int(args.c), int(args.m), int(args.u), args.f )
    gen_banks = gen_all[0]
    gen_ccs = gen_all[1]
    gen_mercs = gen_all[2]
    gen_users = gen_all[3]
    if int(args.p) == 0:
        populate_db = False
    else:
        populate_db = True
    if int(args.r) == 0:
        return_all = False
    else:
        return_all = True
    current_component = handle_current_component( gen_all, args.w, int(args.b), int(args.c), int(args.m), populate_db, return_all )
    print( current_component )

if __name__ == "__main__":
    # execute only if run as a script
    main()
