import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  data: {
    person: {},
    type: 'engagement',
    validity: {
      from: ''
    },
    org_unit: {}
  }
}

const actions = {
  MOVE_EMPLOYEE ({commit, state}) {
    return Service.post('/details/edit', [state])
    .then(response => {
      EventBus.$emit('employee-changed')
      commit('log/newWorkLog', { type: 'EMPLOYEE_MOVE', value: response })
      return response.data
    })
    .catch(error => {
      commit('log/newError', { type: 'ERROR', value: error.response.data })
      return error.response.data
    })
  }
}

const mutations = {
  updateField,

  resetFields (state) {
    state.data = {}
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
