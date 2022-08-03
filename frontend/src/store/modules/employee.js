// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import Service from "@/api/HttpCommon"
import { _employee } from "../actions/employee"
import URLSearchParams from "@ungap/url-search-params"

const defaultState = () => {
  return {
    cpr_no: undefined,
    name: undefined,
    user_key: undefined,
    uuid: undefined,
    org: undefined,
    details: {},
  }
}
const state = defaultState

const ShowIfInherited = (content) => {
  if (content.key === "owner") {
    /* show if inherited */
    if (content.value) {
      content.value.forEach((element) => {
        if (element.owner_inference_priority) {
          if (element.owner) {
            element.owner.name += " (*)"
          }
        }
      })
    }
  }
  return content
}

const actions = {
  [_employee.actions.SET_EMPLOYEE]({ commit }, payload) {
    return Service.get(`/e/${payload}/`)
      .then((response) => {
        commit(_employee.mutations.SET_EMPLOYEE, response.data)
        return response.data
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },

  [_employee.actions.SET_DETAIL]({ state, commit }, payload) {
    let endpoint_name = payload.detail
    let uuid = payload.uuid || state.uuid

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

    // Handle special IT association special case
    if (payload.detail === "itassociation") {
      params.append("it", "1")
      endpoint_name = "association"
    }

    return Service.get(`/e/${uuid}/details/${endpoint_name}?${params}`)
      .then((response) => {
        let content = ShowIfInherited({
          key: payload.detail,
          validity: payload.validity,
          value: response.data,
        })
        commit(_employee.mutations.SET_DETAIL, content)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_employee.mutations.SET_EMPLOYEE](state, payload) {
    state.cpr_no = payload.cpr_no
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
    state.org = payload.org
  },

  [_employee.mutations.RESET_EMPLOYEE](state) {
    Object.assign(state, defaultState())
  },

  [_employee.mutations.SET_DETAIL](state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  },
}

const getters = {
  [_employee.getters.GET_EMPLOYEE]: (state) => state,
  [_employee.getters.GET_DETAIL]: (state) => (id) => state.details[id] || {},
  [_employee.getters.GET_DETAILS]: (state) => state.details || {},
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
