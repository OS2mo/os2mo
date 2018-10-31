import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  original: null,
  move: {
    type: 'engagement',
    data: {
      person: {},
      validity: {
        from: ''
      }
    }
  },
  backendValidationError: null
}

const actions = {
  MOVE_EMPLOYEE ({commit}) {
    state.move.uuid = state.original.uuid

    return Service.post('/details/edit', [state.move])
    .then(response => {
      EventBus.$emit('employee-changed')
      commit('log/newWorkLog', { type: 'EMPLOYEE_MOVE', value: response.data }, { root: true })
      return response.data
    })
    .catch(error => {
      commit('log/newError', { type: 'ERROR', value: error.response.data }, { root: true })
      return error.response.data
    })
  },

  resetFields ({ commit }) {
    commit('resetFields')
  }
}

const mutations = {
  updateField,

  resetFields (state) {
    state.move.data.person = {}
    state.move.data.org_unit = {}
    state.move.data.validity = {}
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
