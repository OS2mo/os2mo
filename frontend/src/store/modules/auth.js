// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { _auth } from '../actions/auth'

const state = {
  accessToken: sessionStorage.getItem('access_token') || '',
  username: null,
  status: ''
}

const actions = {
  [_auth.actions.AUTH_REQUEST]: () => {
    window.location.href = '/saml/sso/?next=' + window.location
  },

  [_auth.actions.AUTH_LOGOUT]: () => {
    window.location.href = '/saml/slo/'
  }
}

const mutations = {
  [_auth.mutations.AUTH_LOGOUT] (state) {
    state.accessToken = ''
    state.username = ''
  },

  [_auth.mutations.AUTH_SUCCESS]: (state, data) => {
    state.accessToken = data.token
    state.username = data.username
    state.status = ''
  },

  [_auth.mutations.AUTH_ERROR]: (state, key) => {
    state.status = key
  }
}

const getters = {
  [_auth.getters.GET_USERNAME]: state => state.username,
  [_auth.getters.GET_STATUS]: state => state.status,
  [_auth.getters.IS_AUTHENTICATED]: state => !!state.accessToken,
  [_auth.getters.GET_ACCESS_TOKEN]: state => state.accessToken
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
