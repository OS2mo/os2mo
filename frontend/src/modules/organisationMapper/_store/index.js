import Service from '@/api/HttpCommon'

const state = {
  origin: undefined,
  destination: []
}

const actions = {
  MAP_ORGANISATIONS ({ state }) {
    console.log(`Map ${state.origin} to ${state.destination}`)
    // Service.post(`/map/${state.origin}`, state.destination)
    //   .then(response => {
    //     console.log('submitted, everything is great')
    //   })
  },

  GET_ORGANISATION_MAPPINGS ({ state, commit }) {
    console.log('getting mappings')
    Service.get(`/ou/${state.origin}/details/related_unit`)
      .then(response => {
        const unitids = []

        for (const relation of response.data) {
          for (const unit of relation.org_unit) {
            if (unit.uuid !== state.origin) {
              unitids.push(unit.uuid)
            }
          }
        }

        commit('SET_DESTINATION', unitids)
      })
  }
}

const mutations = {
  SET_ORIGIN (state, uuid) {
    state.origin = uuid
  },

  SET_DESTINATION (state, uuidList) {
    state.destination = uuidList
  }
}

const getters = {
  origin: state => state.origin,
  destination: state => state.destination
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
