// import Service from '@/api/HttpCommon'

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
    let dummy = ['762b30b0-d92d-4393-a126-884fe7845b9f', 'd3a9e589-5be0-4d28-95af-5d24ac42a2e9']
    commit('SET_DESTINATION', dummy)
    // Service.get(`map/${state.origin}`)
    //   .then(response => {
    //     console.log('got all related uuids')
    //     commit('SET_DESTINATION', response)
    // })
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
  getUuid: state => state.uuid,
  get: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
