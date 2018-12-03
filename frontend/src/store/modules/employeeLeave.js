import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  employee: {},
  leave: {},
  isLoading: false,
  backendValidationError: null
}

const actions = {
  leaveEmployee ({ commit, state }) {
    let payload = state.leave
    payload.person = state.employee

    commit('updateIsLoading', true)

    /**
     * @todo: all create calls are shared now. refactor to one central handler
     */
    return Service.post('/details/create', [payload])
      .then(response => {
        if (response.data.error) {
          commit('updateIsLoading', false)
          commit('updateError', response.data)
          return response.data
        }
        EventBus.$emit('employee-changed')
        commit('resetFields')
        commit('log/newWorkLog', { type: 'EMPLOYEE_LEAVE', value: response.data }, { root: true })
        return response.data
      })
      .catch(error => {
        EventBus.$emit('employee-changed')
        commit('updateIsLoading', false)
        commit('updateError', error.response.data)
        commit('log/newError', { type: 'ERROR', value: error.response.data }, { root: true })
        return error
      })
  },

  resetFields ({ commit }) {
    commit('resetFields')
  }
}

const mutations = {
  updateField,

  updateError (state, error) {
    state.backendValidationError = error
  },

  updateIsLoading (state, isLoading) {
    state.isLoading = isLoading
  },

  resetFields (state) {
    state.employee = {}
    state.leave = {}
    state.backendValidationError = null
  }
}

const getters = {
  getField
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
