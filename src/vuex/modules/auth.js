
import { AUTH_LOGOUT, AUTH_REQUEST, AUTH_SUCCESS, AUTH_ERROR } from '../actions/auth'
import Service from '@/api/HttpCommon'

const state = {
  accessToken: sessionStorage.getItem('access_token') || '',
  username: sessionStorage.getItem('username') || '',
  status: ''
}

const mutations = {
  [AUTH_LOGOUT] (state) {
    state.accessToken = ''
    state.username = ''
  },

  [AUTH_SUCCESS]: (state, data) => {
    state.accessToken = data.token
    state.username = data.username
    state.status = ''
  },

  [AUTH_ERROR]: (state, key) => {
    state.status = key
  }
}

const actions = {
  setAccessToken (state, token) {
    if (token == null) return
    sessionStorage.setItem('access_token', token)
  },

  [AUTH_REQUEST]: ({commit}, user) => {
    return new Promise((resolve, reject) => {
      Service.post('/user/login', user)
        .then(resp => {
          const token = resp.data.token
          const username = resp.data.user
          sessionStorage.setItem('access_token', token)
          sessionStorage.setItem('username', username)
          commit(AUTH_SUCCESS, {token: token, username: username})
          resolve(resp)
        })
        .catch(err => {
          commit(AUTH_ERROR, err.response.data.error_key)
          sessionStorage.removeItem(AUTH_REQUEST)
          reject(err)
        })
    })
  },

  [AUTH_LOGOUT]: ({commit, dispatch}, user) => {
    return new Promise((resolve, reject) => {
      Service.post('/user/logout', user)
      commit(AUTH_LOGOUT)
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('username')
      resolve()
      .then(response => {
        window.location = '/login'
      })
    })
  }
}

const getters = {
  isAuthenticated: state => !!state.accessToken,
  accessToken: state => state.accessToken,
  username: state => state.username,
  status: state => state.status
}

export default {
  state,
  mutations,
  actions,
  getters
}
