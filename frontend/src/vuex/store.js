import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
import employee from './modules/employee'
import log from './modules/log'
import organisation from './modules/organisation'
import organisationUnit from './modules/organisationUnit'
import facet from './modules/facet'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth,
    employee,
    log,
    organisation,
    organisationUnit,
    facet
  }
})
