const state = {
  employee: {
    name: 'Test testensen',
    uuid: 'aaa-bbb-ccc-ddd'
  }
}

const mutations = {
  change (state, employee) {
    state.employee = employee
  }
}

export default {
  namespaced: true,
  state,
  // actions,
  mutations
  // getters
}
