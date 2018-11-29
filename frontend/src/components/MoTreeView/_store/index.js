const state = {
  treeStore: []
}

const actions = {
  updateTree ({ commit }, payload) {
    commit('updateTree', payload)
  }
}

const mutations = {
  updateTree (state, payload) {
    state.treeStore = payload
  }
}

const getters = {
  getTreeData: state => state.treeStore
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
