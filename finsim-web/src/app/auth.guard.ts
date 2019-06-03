<!--
  FinSim
  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
-->

import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';

import { FinSimService } from './fin-sim.service';

@Injectable( { providedIn: 'root' } )
export class AuthGuard implements CanActivate
{
  constructor( private finSimService: FinSimService, private router: Router)
  {}

  canActivate( route: ActivatedRouteSnapshot, state: RouterStateSnapshot )
  {
    var storedToken = localStorage.getItem( 'currentUser' );

    if( storedToken && this.finSimService.amILoggedIn() )
    {
      return true;
    }

    this.router.navigate( ['/login'], { queryParams: { returnUrl: state.url } } );
    return false;
  }
  //canActivate( next: ActivatedRouteSnapshot, state: RouterStateSnapshot) : Observable<boolean>
  //{
  //  return this.finSimService.isLoggedIn.pipe(
  //    take( 1 ),
  //    map( ( isLoggedIn: boolean ) =>
  //    {
  //      if( !isLoggedIn )
  //      {
  //        this.router.navigate( ['/login'] );
  //        return false;
  //      }
  //      return true;
  //    })
  //  );
  //}
}
