import Service from '@/api/HttpCommon'

const state = {
  queries: []
}

const actions = {
  getQueries: ({ commit }) => {
    Service.get('/exports/')
      .then(response => {
        commit('setQueries', response.data)
      })
  },

  downloadFile ({ commit }, fileName) {
    Service.get(`/exports/${fileName}`, { 'responseType': 'blob' })
      .then(response => {
        const blob = new Blob([response.data])
        if (window.navigator.msSaveBlob) { // internet explorer
          window.navigator.msSaveOrOpenBlob(blob, fileName)
        } else {
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', fileName)
          document.body.appendChild(link)
          link.click()
        }
      })
  }
}

const mutations = {
  setQueries (store, payload) {
    store.queries = payload
  }
}

const getters = {
  getQueries: state => state.queries
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
