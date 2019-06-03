FinSim

Copyright 2018 Carnegie Mellon University. All Rights Reserved.

NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.

Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

# FinSim Web

## Brief:
- FinSim-web is the frontend for the transaction server - allows users to access accounts to view balances and transaction logs with a web browser
- This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 6.0.8.

## Quick Usage:

### For development environments, see below

- Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.
- Make sure to check the url used in `/src/app/fin-sim-service.ts` as that is used by web for login/account details
    - finsim-trans and web run on the same machine but web still sends web requests to trans for functionality

#### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

#### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

#### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

#### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).


### For production environments, see below

- Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Overview:

### /e2e
- end to end testing via Protractor
- [TODO] Need to add more to make testing finsim-web easier

### /src

#### /app
- Available routes:
    - /login: Login with a registered username and password to get access to the user's information
        - If successful, routed to the specific user's /accounts page
    - /account?number=: Prints out the specific account's id/number/balance and a list of transactions the account is involved in
    - /accounts: Lists all of the accounts that the user (that is logged in) owns for this bank
        - Each account has a link to it's specific account details page
            - Routes to /account?number=xxxxxxxxxxxxxxxx
- Components used:
    - account-details: Used for /account?number= functionality
    - accounts: Used for /accounts functionality
    - admin-dashboard: Used for banks to login and see accounts
    - interceptors: Used for AuthGuard/authentication purposes (prevent a user that has not logged in from accessing more than just the login page
    - login: Used for /login functionality
    - header: Header used overall

