<!--
  FinSim
  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
-->

import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot } from '@angular/router';
import { FinSimService } from './fin-sim.service';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { decode } from 'jwt-decode';
import { of } from 'rxjs';

@Injectable()
export class RoleGuardService implements CanActivate
{
  constructor( public finSimService: FinSimService, public router: Router )
  {}

  canActivate( route: ActivatedRouteSnapshot ): Observable<boolean>
  {
    console.log( "INSIDE ROLE GUARD CAN-ACTIVATE FUNCTION" );
    let accessToken = this.finSimService.getAccessToken();
    if( accessToken === null )
    {
      this.router.navigate( ['/login'] );
      return of( false );
    }

    if( !this.finSimService.amILoggedIn() )
    {
      console.log( "ROLE GUARD redirecting to login page..." );
      this.router.navigate( ['/login'] );
      return of( false );
    }

    let authorities = accessToken.authorities;
    console.log( accessToken.identity.role );

    const expectedRole = route.data.expectedRole;

    if( expectedRole == accessToken.identity.role )
    {
      return of( true );
    }

    this.router.navigate( ['/login'] );
    return of( false );
  }
}
