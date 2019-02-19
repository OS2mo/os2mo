import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
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
Vue.use(Vuex)

export default new Vuex.Store({
  // strict: true,
  modules: {
    [Auth.NAMESPACE]: auth,
    [Employee.NAMESPACE]: employee,
    log: log,
    [Organisation.NAMESPACE]: organisation,
    [OrganisationUnit.NAMESPACE]: organisationUnit,
    [Facet.NAMESPACE]: facet
  }
})
