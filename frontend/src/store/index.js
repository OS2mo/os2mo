import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
import employee from './modules/employee'
import log from './modules/log'
import organisation from './modules/organisation'
import organisationUnit from './modules/organisationUnit'
import employeeLeave from './modules/employeeLeave'
import employeeMove from './modules/employeeMove'
import employeeTerminate from './modules/employeeTerminate'
import facet from './modules/facet'

Vue.use(Vuex)

export default new Vuex.Store({
  // strict: true,
  modules: {
    auth: auth,
    employee: employee,
    log: log,
    organisation: organisation,
    organisationUnit: organisationUnit,
    employeeLeave: employeeLeave,
    employeeMove: employeeMove,
    employeeTerminate: employeeTerminate,
    facet: facet
  }
})
