// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import Service from "@/api/HttpCommon"
import Facet from "@/api/Facet"
import { _facet } from "../actions/facet"

const state = {
  org_unit_address_type: undefined,
  employee_address_type: undefined,
  manager_address_type: undefined,
  visibility: undefined,
  association_type: undefined,
  engagement_type: undefined,
  engagement_job_function: undefined,
  leave_type: undefined,
  manager_level: undefined,
  manager_type: undefined,
  org_unit_type: undefined,
  responsibility: undefined,
  role_type: undefined,
  org_unit_hierarchy: undefined,
  primary_type: undefined,
}

const fullQueryParams =
  "?" +
  [
    Facet.ClassDetails.FULL_NAME,
    Facet.ClassDetails.TOP_LEVEL_FACET,
    Facet.ClassDetails.FACET,
  ].join("&")

const actions = {
  [_facet.actions.SET_FACET]({ rootState, commit }, payload) {
    let queryParams = ""
    if (payload.full) {
      queryParams = fullQueryParams
    }
    if (rootState.organisation.uuid == undefined) return
    return Service.get(
      `/o/${rootState.organisation.uuid}/f/${payload.facet}/${queryParams}`
    )
      .then((response) => {
        response.data.classes = response.data.data.items
        delete response.data.data.items
        commit(_facet.mutations.SET_FACET, response.data)
        return response.data
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_facet.mutations.SET_FACET](state, payload) {
    state.uuid = payload.uuid
    Vue.set(state, payload.user_key, payload)
    Vue.set(state, payload.uuid, payload)
  },
}

const getters = {
  [_facet.getters.GET_UUID]: (state) => state.uuid,
  [_facet.getters.GET_FACET]: (state) => (id) => {
    return state[id] ? state[id] : {}
  },
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
