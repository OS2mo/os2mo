import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus, Events } from '@/EventBus'

const defaultState = () => {
  return {
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
}

const state = defaultState

const actions = {
  MOVE_EMPLOYEE ({ commit, state }) {
    state.move.uuid = state.original.uuid

    return Service.post('/details/edit', state.move)
      .then(response => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit('log/newWorkLog',
          { type: 'EMPLOYEE_MOVE', value: response.data },
          { root: true })
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
    Object.assign(state, defaultState())
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
