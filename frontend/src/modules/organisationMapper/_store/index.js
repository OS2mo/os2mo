import moment from 'moment'
import Service from '@/api/HttpCommon'

const state = {
  origin: undefined,
  destination: [],
  raw_destination: []
}

const actions = {
  MAP_ORGANISATIONS ({ state }) {
    console.log(`Map ${state.origin} to: ${state.destination.join(', ')}`)

    Service.post(`/ou/${state.origin}/map`,
                 {
                   destination: state.destination,
                   validity: {
                     from: moment().format('YYYY-MM-DD')
                   }
                 },
                )
      .then(response => {
        console.log('submitted, everything is great')
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
  original_destination: state => state.raw_destination.flatMap(
    func => func.org_unit.map(ou => ou.uuid).filter(id => id !== state.origin)
  )
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
