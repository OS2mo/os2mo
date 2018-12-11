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
