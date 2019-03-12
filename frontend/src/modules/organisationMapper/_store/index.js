import isEqual from 'lodash.isequal'
import moment from 'moment'
import Service from '@/api/HttpCommon'

const state = {
  origin: undefined,
  destination: [],
  raw_destination: []
}

const actions = {
  MAP_ORGANISATIONS ({ commit, dispatch, state }) {
    Service.post(
      `/ou/${state.origin}/map`,
      {
        destination: state.destination,
        validity: {
          from: moment().format('YYYY-MM-DD')
        }
      }
    )
      .then(result => {
        commit('log/newWorkLog',
          { type: 'ORGANISATION_EDIT', value: state.origin },
          { root: true })

        dispatch('GET_ORGANISATION_MAPPINGS')
      })
      .catch(error => {
        commit('log/newError',
          { type: 'ERROR', value: error.response },
          { root: true })
        return error
      })
  },

  GET_ORGANISATION_MAPPINGS ({ state, commit }) {
    Service.get(`/ou/${state.origin}/details/related_unit`)
      .then(response => {
        commit('SET_RAW_DESTINATION', response.data)
      })
  }
}

const mutations = {
  SET_ORIGIN (state, uuid) {
    state.origin = uuid
  },

  SET_RAW_DESTINATION (state, response) {
    state.raw_destination = response
    state.destination = response.flatMap(
      func => func.org_unit.map(ou => ou.uuid).filter(
        id => id !== state.origin
      )
    )
  },

  SET_DESTINATION (state, uuidList) {
    state.destination = Array.from(uuidList)
  }
}

const getters = {
  origin: state => state.origin,
  destination: state => state.destination,
  isDirty: state => {
    let orig = new Set(
      state.raw_destination.flatMap(
        func => func.org_unit.map(ou => ou.uuid).filter(id => id !== state.origin)
      )
    )
    return !isEqual(new Set(state.destination), orig)
  }
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
