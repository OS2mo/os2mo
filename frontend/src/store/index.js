// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
import conf from './modules/conf'
import employee from './modules/employee'
import log from './modules/log'
import organisation from './modules/organisation'
import organisationUnit from './modules/organisationUnit'
import facet from './modules/facet'
import { Employee } from './actions/employee'
import { OrganisationUnit } from './actions/organisationUnit'
import { Facet } from './actions/facet'
import { Organisation } from './actions/organisation'
import { Auth } from './actions/auth'
import { Conf } from './actions/conf'
Vue.use(Vuex)

export default new Vuex.Store({
  // strict: true,
  modules: {
    [Conf.NAMESPACE]: conf,
    [Auth.NAMESPACE]: auth,
    [Employee.NAMESPACE]: employee,
    log: log,
    [Organisation.NAMESPACE]: organisation,
    [OrganisationUnit.NAMESPACE]: organisationUnit,
    [Facet.NAMESPACE]: facet
  }
})
