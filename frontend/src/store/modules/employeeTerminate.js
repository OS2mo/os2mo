import Vue from 'vue'
import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  employee: {},
  endDate: '',
  details: {}
}

const actions = {
  TERMINATE_EMPLOYEE ({ state, commit, dispatch }) {
    let payload = {
      validity: {
        to: state.endDate
      }
    }
    return Service.post(`/e/${state.employee.uuid}/terminate`, payload)
      .then(response => {
        EventBus.$emit('employee-changed')
        commit('log/newWorkLog', { type: 'EMPLOYEE_TERMINATE', value: response.data }, { root: true })
        dispatch('resetFields')
        return response.data
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
        return error.response.data
      })
  },

  // TODO: copypaste from the employee module. Need to be refactored
  setDetails ({ state, commit }, payload) {
    payload.validity = payload.validity || 'present'
    let uuid = payload.uuid || state.employee.uuid
    return Service.get(`/e/${uuid}/details/${payload.detail}?validity=${payload.validity}`)
      .then(response => {
        let content = {
          key: payload.detail,
          validity: payload.validity,
          value: response.data
        }
        commit('setDetail', content)
      })
      .catch(error => {
        console.log(error)
      })
  },

  resetFields ({ commit }) {
    commit('resetFields')
  }
}

const mutations = {
  updateField,

  resetFields (state) {
    state.employee = {}
    state.endDate = ''
    state.details = {}
  },

  // todo: copy paste from employee module. need to be refactored
  setDetail (state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  }
}

const getters = {
  getField,
  getDetails: (state) => state.details || {}
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
