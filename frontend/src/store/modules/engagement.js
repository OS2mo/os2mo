// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import Service from "@/api/HttpCommon"
import { _engagement } from "../actions/engagement"
import URLSearchParams from "@ungap/url-search-params"

const defaultState = () => {
  return {
    user_key: undefined,
    uuid: undefined,
    org: undefined,

    details: {},
  }
}
const state = defaultState

const actions = {
  [_engagement.actions.SET_ENGAGEMENT]({ commit }, payload) {
    return Service.api_v1_get(`/engagement/by_uuid?uuid=${payload}`)
      .then((response) => {
        commit(
          _engagement.mutations.SET_ENGAGEMENT,
          response.data.length ? response.data[0] : {}
        )
        return response.data
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },

  [_engagement.actions.SET_DETAIL]({ state, commit }, payload) {
    let uuid = payload.uuid
    // Build query string from payload
    const params = new URLSearchParams()
    params.append("validity", payload.validity || "present")
    if (payload.atDate) {
      params.append("at", payload.atDate)
    }
    if (payload.extra !== undefined) {
      for (const key in payload.extra) {
        params.append(key, payload.extra[key])
      }
    }

    // special handling if we're asking about our own id
    let path = `/${payload.detail}`
    if (payload.detail === "engagement" && uuid) {
      path += "/by_uuid"
      params.append("uuid", uuid)
    } else if (uuid) {
      params.append("engagement", uuid)
    }
    // Service.get(`/e/23d2dfc7-6ceb-47cf-97ed-db6beadcb09b/details/${payload.detail}?${params}`)
    return Service.api_v1_get(`${path}?${params}`)
      .then((response) => {
        let content = {
          key: payload.detail,
          validity: payload.validity,
          value: response.data,
        }
        commit(_engagement.mutations.SET_DETAIL, content)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_engagement.mutations.SET_ENGAGEMENT](state, payload) {
    state.user_key = payload.user_key
    state.uuid = payload.uuid
    state.org = payload.org
  },

  [_engagement.mutations.RESET_ENGAGEMENT](state) {
    Object.assign(state, defaultState())
  },

  [_engagement.mutations.SET_DETAIL](state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  },
}

const getters = {
  [_engagement.getters.GET_ENGAGEMENT]: (state) => state,
  [_engagement.getters.GET_DETAIL]: (state) => (id) => state.details[id] || {},
  [_engagement.getters.GET_DETAILS]: (state) => state.details || {},
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
