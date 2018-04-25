import Vue from 'vue'
import Vuex from 'vuex'
import employee from './modules/employee'
import log from './modules/log'
import organisation from './modules/organisation'
import organisationUnit from './modules/organisationUnit'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    employee: employee,
    log: log,
    organisation: organisation,
    organisationUnit: organisationUnit
  }
})
